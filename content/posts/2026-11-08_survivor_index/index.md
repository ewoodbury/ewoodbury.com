---
title: "Faster data processing with zero-copy filters"
date: 2026-11-08
draft: true
---

Consider a simple filter operation passed to a data processing engine:
```
val highEarners = salaries.filter(_.salary > 100000).collect()
```

A simple query engine executes this by first allocating a new location in memory for the result data. Then it pulls the the original data from memory into the caches and then CPU, evaluates the filter, then copies only passing records into the allocated destination in memory.
```
For a dataset of [employee, salary] pairs:
(["Joe", 85000], ["Sally", 120000], ["Allen", 140000], ["Linda", 95000], ["Tony", 80000])

Engine allocates new destination in memory: 
(<blank>, <blank>, <blank>, <blank>, <blank>)

Then fills it with surviving data:
(["Sally", 120000], ["Allen", 140000], <blank>, <blank>, <blank>)
```

To do the memory allocation, the program doesn't know how many records will survive, so it allocates the new buffer as the same size as the entire input dataset in case all records pass the filter. Memory usage is doubled during the operation until the original data can be freed.

What about ano? Or even more? Same idea - program needs to allocate a buffer in memory for every new filter result, and copy data into it after each operation. For the subsequent query:
```scala
val highEarnersA = salaries.filter(_.salary > 100000).filter(_.name[0] == "A")
```
```
Filtered to employees with names starting with 'A':
(["Allen", 140000], <blank>)
```

The naive query engine implemenation is as follows:
```scala
code
````

This approach is straightforward and trivially correct. However the additional memory required and scans leave room for improvement. 

## Survivor Indices

Instead of allocating a buffer the size of the whole dataset and copying the entire survivor dataset, it can instead decide to track only row numbers of the survivor records. 
```
For a dataset of [employee, salary] pairs:
(["Joe", 85000], ["Sally", 120000], ["Allen", 140000], ["Linda", 95000])

Filtered to employees with salary > 100000, saving only surivor indexes
(1, 2, <blank>, <blank>)
```

In this case, the engine only allocates space for 4 `int32`s, or 16 bytes total. The large name string does not have an impact on memory usage. 

Subsequent filters can operate directly on the indexes as well, using the index as a lookup.
```
Original Dataset: (["Joe", 85000], ["Sally", 120000], ["Allen", 140000], ["Linda", 95000])
Current survivors: (1, 2, <blank>, <blank>)

Filtered to employees with names starting with 'A':
(2, <blank>)
```
A tradeoff on this subsequent filter is the extra time spent to do the record lookups based on the indexes. The program needs to fetch the full record from the original array in memory for records 1 and 2 to do the name filter.

The optimized query engine with survivor indices is:
```scala
code
````


## Count and sum

Now consider the following sum operation:
```
salaries.filter(_ > 100000).sum()
```

Following these optimizations, an engine could save the survivor indices only throughout the computation, then do fast array lookups at the end to aggregate the total. This beats the naive approach of allocating an entire new array of the same original size.

```
(["Joe", 85000], ["Sally", 120000], ["Allen", 140000], ["Linda", 95000], ["Tony", 80000])

Filter salary > 100000, survivor indices
(1, 2, <blank>, <blank>, <blank>)

Calculate final sum:
salary[1] + salary[2] = 120000 + 140000 = 260000
```

However, aggregations do not require any of the original data to be returned at the end, which unlocks a further optimized physical execution plan.

The engine can instead aggregate as it goes, so it only needs to allocate space for one additional value, and it calculates during the single scan over the original data. If the program parallelizes execution over multiple batches, each batch can have its own sum calculated, and all sums are then combined at the end. Each row is only ever touched one time.

```
(["Joe", 85000], ["Sally", 120000], ["Allen", 140000], ["Linda", 95000], ["Tony", 80000])

Single scan, aggregating total as we go:
  skip...         total=120000...    total=160000...     skip...          skip...

Return: total = 260000
```

Optimized query engine:
...

## Results


## Wrap-up

Query engines are a neat way to see data structures and algorithm principles applied in real life. These optimizations are elementary, but they're illustrative of the thousands of techniques that make up the database engines that run the world.

A related and slightly more advanced technique is operator fusing, which involves automatically optimizing chained filters into a single operation. Similarly x, y, and z are other optimizations that improve execution on simple queries like this. I may cover these in a future post!

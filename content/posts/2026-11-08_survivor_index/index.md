---
title: "Faster data processing with zero-copy filters"
date: 2026-11-08
draft: true
---

Simple filter: pull data from memory into the CPU, check whether it meets the condition, copy survivor records into a new array. 

```
For a dataset of [employee, salary] pairs:
(["Joe", 85000], ["Sally", 120000], ["Allen", 140000], ["Linda", 95000])

Filtered to employees with salary > 100000:
(["Sally", 120000], ["Allen", 140000], <blank>, <blank>)
```

The program needs to allocate space in memory for the result data upfront. However, because the program doesn't know how many records will survive, and all records could pass the filter, the program allocates a buffer the same size as the entire input dataset to be safe. Memory usage is doubled during the operation until the original data can be freed.

What about two filters? Or even more? Same idea - program needs to allocate a buffer in memory for every new filter result, and copy data into it after each operation. 

```
Filtered to employees with names starting with 'A':
(["Allen", 140000], <blank>)
```

(There's also operator fusing, which involves automatically optimizing chained filters into a single operation, but we'll leave that for a future blog.)

We can easily beat this approach though, using a slightly smarter technique!

Record Indexing

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


## Count and sum

What about for aggregations, like counts or sums? Following our existing optimized approach, an engine could 

However, aggregations do not require any of the original data to be returned at the end, which actually unlocks a further optimized physical execution plan.



## The copies

- Counting 1,000,000 filtered pairs allocated 23.4 MB before this and 8.3 MB after, which is the two source columns.

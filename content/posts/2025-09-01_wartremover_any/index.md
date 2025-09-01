---
title: "Safer Scala with WartRemover Part 2: A Basic Guide to remove Any types"
date: 2025-08-31
draft: true
---

This is the second in a series of posts about improving the Scala code quality, and using [WartRemover](https://www.wartremover.org/) as the static analysis tool to enforce these best practices.

The WartRemover Any rule is straightfoward; it bans the use of the `Any` type, including `AnyVal` and `AnyRef`.

I'll use this post to show a couple interesting cases where I've used Scala's type system to model complex programs correctly, and thus avoid `Any`.

---
### 1. Basic Example

Let's write a simple [polymorphic method](https://docs.scala-lang.org/tour/polymorphic-methods.html) that processes different types of data. The naive implementation uses `Any`:
```scala
def findLexicographicalMax(items: List[Any]): Any = {
  items.reduce((a, b) => if (a.toString > b.toString) a else b)
}
```

This compiles but loses type safety - we can accidentally pass mixed types:
```scala
val mixed = List("hello", 42, 3.14, List(1, 2))
findLexicographicalMax(mixed) // Throws RuntimeException at runtime for 3.14 and List(1, 2)
```
Instead, we can use a generic type parameter to work with any type, as long as all elements are the same:
```scala
def findLexicographicalMax[T](items: List[T])(implicit ord: Ordering[T]): T = {
  items.reduce(ord.max)
}
```
Now the function works with any homogeneous list, and mixed types are caught at compile time:
```scala
val strings = List("hello", "world")
findLexicographicalMax(strings) // Returns "world"

val numbers = List(1, 2, 3)
findLexicographicalMax(numbers) // Returns 3

val mixed = List("hello", 42) // Compile error: type mismatch
```

Bonus: If we want to support multiple types in a single input, we can use Scala 3's new [union types](https://docs.scala-lang.org/scala3/book/types-union.html):
```scala
def findMaxUnion(items: List[Int | String | Double]): Int | String | Double = {
  items.maxBy {
    case i: Int => i.toString
    case s: String => s
    case d: Double => f"$d%.2f"
  }
}

val mixed = List(42, "hello", 3.14)
findMaxUnion(mixed) // Returns "hello"

val mixedUnsupported = List(42, "hello", List(1, 2)) 
// Compile error: List(1, 2) is not Int | String | Double
```

### 2. More Complex Example

Here's a more complex example from my real-world [Sparklet](https://github.com/ewoodbury/sparklet) project, a rebuild of Spark in Scala 3.

In Sparklet, we have a distinct set of operations that can be applied:
```scala
---
title: "Safer Scala with WartRemover Part 2: A Basic Guide to Removing Any"
date: 2025-08-31
draft: true
---

This is the second in a series of posts about improving the Scala code quality, and using [WartRemover](https://www.wartremover.org/) as the static analysis tool to enforce these best practices.

The WartRemover Any rule is straightfoward; it bans the use of the `Any` type, including `AnyVal` and `AnyRef`.

See [Part 1](https://ewoodbury.com/posts/2025-08-25_head_seq_apply_wartremover/) for how to set up WartRemover. Once you're set up, simply add the following to your `build.sbt`:
```scala
wartremoverErrors += WartRemover.warts.Any
```

I'll use this post to show a couple interesting cases where I've used Scala's type system to model complex programs correctly, and thus either remove `Any` or at least isolate its usage to a small surface area.

---
### 1. Basic Example

Let's write a simple [polymorphic method](https://docs.scala-lang.org/tour/polymorphic-methods.html) that processes either numbers or strings to find the first value in lexicographical order (alphabetically). The naive implementation uses `Any`:
```scala
def findLexicographicalMax(items: List[Any]): Any = {
  items.reduce((a, b) => if (a.toString > b.toString) a else b)
}
```

This compiles but loses type safety: we can accidentally pass mixed types and get a runtime error:
```scala
val mixed = List("hello", 42, 3.14, List(1, 2))
findLexicographicalMax(mixed) // Throws RuntimeException at runtime for 3.14 and List(1, 2)
```
Instead, we can use a generic type parameter to work with any type, as long as all elements within the call are the same:
```scala
def findLexicographicalMax[T](items: List[T])(implicit ord: Ordering[T]): T = {
  items.reduce(ord.max)
}
```
The function now works with any homogeneous list, and mixed types are caught at compile time:
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
findMaxUnion(mixedUnsupported)
// Compile error: Required List[Int | String | Double]
```

### 2. More Complex Example

Here's a more complex example from my real-world [Sparklet](https://github.com/ewoodbury/sparklet) project, a rebuild of Spark in Scala 3.

In Sparklet, we neeed to generate job processing stages based on one of many possible transformations. An extremely naive implementation might use Any to handle the different transformation types, and thus have type erasure issues:
```scala
def processOperation(op: Any): Any = {
  // We have no idea what operations are valid
  // Pattern matching is unsafe and incomplete
  op match {
    case f: Function1[_, _] => f.asInstanceOf[Any => Any] // Unsafe casting everywhere!
    case _ => throw new RuntimeException("Unknown operation")
  }
}
```
Here's a better approach using a sealed trait, which is extended by each operation:
```scala
sealed trait Operation[A, B]

// Narrow transformations
final case class MapOp[A, B](f: A => B) extends Operation[A, B]
final case class FilterOp[A](p: A => Boolean) extends Operation[A, A]
final case class FlatMapOp[A, B](f: A => IterableOnce[B]) extends Operation[A, B]

// Key-value operations
final case class KeysOp[K, V]() extends Operation[(K, V), K]
final case class ValuesOp[K, V]() extends Operation[(K, V), V]
final case class MapValuesOp[K, V, V2](f: V => V2) extends Operation[(K, V), (K, V2)]

def processOperation[A, B](op: Operation[A, B]): String = op match {
  case MapOp(f) => s"Map operation with function: $f"
  case FilterOp(p) => s"Filter operation with predicate: $p" 
  case FlatMapOp(f) => s"FlatMap operation with function: $f"
  case KeysOp() => "Extract keys from key-value pairs"
  case ValuesOp() => "Extract values from key-value pairs"
  case MapValuesOp(f) => s"Map values with function: $f"
}
```

Link to Sparklet code: [Operations.scala](https://github.com/ewoodbury/sparklet/blob/0f9be0bf03a99c8721096e014ef64ea501faefe8/modules/sparklet-execution/src/main/scala/com/ewoodbury/sparklet/execution/Operation.scala)

### 3. When Any is Unavoidable

Here's another example from stage building, where we need to handle multiple operation types that have been type-erased to `Operation[Any, Any]` at runtime. The problematic approach scatters unsafe casting throughout the core transofromation logic:

```scala
private def createStageFromOp(op: Operation[Any, Any]): Stage[Any, Any] = {
  op match {
    case KeysOp() => Stage.keys[Any, Any].asInstanceOf[Stage[Any, Any]] // Unsafe casting scattered everywhere
    case ValuesOp() => Stage.values[Any, Any].asInstanceOf[Stage[Any, Any]] // Hard to audit safety
    case MapValuesOp(f) => Stage.mapValues[Any, Any, Any](f).asInstanceOf[Stage[Any, Any]] // Repetitive and error-prone
    case MapOp(f) => Stage.map(f)
    case FilterOp(p) => Stage.filter(p)
    case FlatMapOp(f) => Stage.flatMap(f)
    // ... other cases
  }
}
```

In this case, `Any` is unavoidable because operations with different type parameters (like `MapOp[String, Int]` and `FilterOp[Double]`) must be stored together in collections and processed together. We're forced to use `Operation[Any, Any]` as a common supertype. Here's how we handle this: 
```scala
// Type-safe stage builders
object StageBuilder {
  def fromOperation[A, B](op: Operation[A, B]): Stage[A, B] = op match {
    case MapOp(f) => Stage.map(f)
    case FilterOp(p) => Stage.filter(p) 
    case FlatMapOp(f) => Stage.flatMap(f)
    case KeysOp() => Stage.keys[A, B] // Type parameters are preserved in core logic
    case ValuesOp() => Stage.values[A, B]
    case MapValuesOp(f) => Stage.mapValues(f)
  }
}

// Ignore WartRemover only for this method
@SuppressWarnings(Array("org.wartremover.warts.Any"))
private def createStageFromOpUnsafe(op: Operation[Any, Any]): Stage[Any, Any] = {
  // Single controlled point of type erasure
  StageBuilder.fromOperation(op)
}
```
Lint to Sparklet code: [StageBuilder.scala](https://github.com/ewoodbury/sparklet/blob/main/modules/sparklet-execution/src/main/scala/com/ewoodbury/sparklet/execution/StageBuilder.scala)

We handle this case by isolating the `Any` usage to a single boundary method, `createStageFromErasedOp`; type safety is preserved elsewhere in the class. We can cover this method with focused testing as a fallback.

A few other examples of when `Any` is necessary would be when using reflection APIs, serialization/deserialization like JSON, or interacting with external systems where types are dynamic.

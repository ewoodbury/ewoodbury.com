---
title: "Safer Scala with WartRemover Part 2: A Basic Guide to Removing Any"
date: 2025-08-31
draft: false
---

This is the second in a series of posts about improving Scala code quality using the WartRemover static analysis tool, and more broadly about language restrictions to improve program correctness.

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

Thanks to Scala 3, we can use the new [union types](https://docs.scala-lang.org/scala3/book/types-union.html) to hold multiple types within the same collection:
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

Here's a more complex example from my real-world [Sparklet](https://github.com/ewoodbury/sparklet) project (a function rebuild of the Spark engine).

In Sparklet, we generate data processing stages based on one of many supported transformations. A naive implementation would use Any to handle different transformation types, which would have the issue of erasing transformation types:
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
Here's a better approach using a sealed trait:
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

Here's another example from Sparklet's stage builder, where we handle operation types that were erased to `Operation[Any, Any]` at runtime. There are unsafe casts all throughout the core logic:

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

This is one of the few locations within Sparklet where `Any` is truly unavoidable, because operations with different types (`MapOp[String, Int]` and `FilterOp[Double]`) must be processed together in a single hetergeneous Scala collection. There's no way to keep the types intact throughout the entire stage building operation; we need to use `Operation[Any, Any]` as a common type instead.

We handle this by isolating the `Any` usage to a boundary method, `createStageFromOpUnsafe`; type safety is preserved elsewhere in the class. Ideally, this unsafe method would be subject to focused unit testing, relying on runtime checks in lieu of compile-time safety.

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

A few other examples of when `Any` is necessary would be when using reflection APIs, serialization/deserialization like JSON, or interacting with external systems where types are dynamic.

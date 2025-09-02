---
title: "Safer Scala with WartRemover Part 1: Seq.apply and head"
date: 2025-08-25
draft: false
---

This is the first of a series of posts about using [WartRemover](https://www.wartremover.org/) to improve the quality of Scala codebases. WartRemover is a static analysis tool for Scala.

I find it useful because it actively disables parts of Scala to improve safety by default. You get the benefits of a stricter language like Rust, while still being able to use `SuppressWarnings` as an escape hatch.

I also like that the warnings often present as a mini programming puzzle. Will I be clever enough to fix it, perhaps even without AI help?

---
Here's a very short reference on setting up WartRemover for your Scala project:

```scala
// plugins.sbt
addSbtPlugin("org.wartremover" % "sbt-wartremover" % "3.3.3")
// any other plugins...
```

```scala
// build.sbt
// Set Warts as warnings (compile can still succeed)
wartremoverWarnings += WartRemover.warts.Any
// Or set Warts as errors (compile fails)
wartremoverErrors += Wart.SeqApply

// Or if you want to include all warts with the exception of a few:
wartremoverWarnings ++= Warts.allBut(
  Wart.ImplicitParameter,
  ...
)
```
Check out the [WartRemover Setup Guide](https://www.wartremover.org/doc/install-setup.html) for more details.

---

Two closely-related Warts are `SeqIndex` and `Head`. These Warts ban the use of `Seq.apply` (i.e. indexing into a sequence with parentheses) and `Seq.head`, since both can throw exceptions at runtime.

### Basic Example

Here's an example of real code from my [Sparklet](https://github.com/ewoodbury/sparklet) project that was caught by this Wart:

```scala
private[execution] def materialize(ops: Vector[Operation]): Stage[Any, Any] = {

    return ops.head match { // WartRemover warning raised: .head is disabled
        case MapOp(f) => Stage.map(f.asInstanceOf[Any => Any])
        case FilterOp(p) => Stage.filter(p.asInstanceOf[Any => Boolean])
        case FlatMapOp(f) => Stage.flatMap(f.asInstanceOf[Any => IterableOnce[Any]])
        ...
```

The fix is simple for this case: check that the sequence is non-empty, and then use `headOption.get`, which is safe because of the prior check.

```scala
private[execution] def materialize(ops: Vector[Operation]): Stage[Any, Any] = {
    require(ops.nonEmpty, "Cannot materialize empty operation vector")

    if (ops.length == 1) {
        return ops.headOption.get match {
        case MapOp(f) => Stage.map(f.asInstanceOf[Any => Any])
        case FilterOp(p) => Stage.filter(p.asInstanceOf[Any => Boolean])
        case FlatMapOp(f) => Stage.flatMap(f.asInstanceOf[Any => IterableOnce[Any]])
        ...
```

Similarly, below is an example of replacing `Seq.apply` with safe alternatives:
```scala
    val shuffleInputSources = meta.kind match {
      case WideOpKind.Join | WideOpKind.CoGroup =>
        Seq(
          // Indexing with meta.sides(0) and meta.sides(1) uses Seq.apply; 
          // this is unsafe if sides has less than 2 elements
          ShuffleInput(upstreamIds(0), Some(meta.sides(0)), meta.numPartitions),
          ShuffleInput(upstreamIds(1), Some(meta.sides(1)), meta.numPartitions)
        )
      case _ =>
        // Single-input operations
        require(upstreamIds.length == 1, s"${meta.kind} requires exactly 1 upstream stage")
        Seq(ShuffleInput(upstreamIds.head, None, meta.numPartitions)) // using head
    }
```
We can avoid the apply by first checking the input sequence with `require`, and then using `take`:
```scala
    val shuffleInputSources = meta.kind match {
      case WideOpKind.Join | WideOpKind.CoGroup =>
        require(upstreamIds.length == 2, s"${meta.kind} requires exactly 2 upstream stages")
        require(meta.sides.length == 2, s"${meta.kind} requires exactly 2 sides")
        
        val List(upstream1, upstream2) = upstreamIds.take(2).toList
        val List(side1, side2) = meta.sides.take(2).toList
        
        Seq(
          ShuffleInput(upstream1, Some(side1), meta.numPartitions),
          ShuffleInput(upstream2, Some(side2), meta.numPartitions)
        )
      case _ =>
        // Single-input operations
        require(upstreamIds.nonEmpty, s"${meta.kind} requires exactly 1 upstream stage")
        Seq(ShuffleInput(upstreamIds.headOption.get, None, meta.numPartitions))
    }
```

Of course, the `require` can still throw the exception for an emtpy sequence, but this fails fast and is easier to debug than a `NoSuchElementException`.


### More Complex Example

The value is perhaps best demonstrated in a more complex case, where having WartRemover restrict `head` and `apply` forces a larger refactor, improving safety significantly.

Consider this Spark pipeline:
```scala
import org.apache.spark.sql.{DataFrame, Column}
import org.apache.spark.sql.functions._

case class JoinSpec(leftCol: String, rightCol: String, joinType: String)

def buildDataPipeline(tables: Vector[DataFrame], 
                     joinSpecs: Vector[JoinSpec], 
                     groupByCols: Vector[String]): DataFrame = {
  
  // Unsafe: could throw if empty
  val baseDf = tables.head
  val joinDfs = tables.tail
  
  // Build joins - unsafe indexing
  val joinedDf = joinSpecs.zipWithIndex.foldLeft(baseDf) { case (df, (spec, idx)) =>
    df.join(joinDfs(idx), col(spec.leftCol) === col(spec.rightCol), spec.joinType)  // Unsafe indexing
  }
  
  // Group by - unsafe head access
  val primaryGroupCol = groupByCols.head  // Unsafe
  val restGroupCols = groupByCols.tail.map(col)
  
  joinedDf
    .groupBy(col(primaryGroupCol), restGroupCols: _*)
    .agg(count("*").as("record_count"), sum(col(groupByCols(0))).as("total"))  // Unsafe indexing
}
```

We can improve this by removing the unsafe `head` and `apply` indexing cols, and by using a functional for-comprehension with `Either` to handle runtime errors cleanly:
<!-- ```scala
import org.apache.spark.sql.{DataFrame, Column}
import org.apache.spark.sql.functions._

case class JoinSpec(leftCol: String, rightCol: String, joinType: String)

def buildDataPipeline(tables: Vector[DataFrame], 
                     joinSpecs: Vector[JoinSpec], 
                     groupByCols: Vector[String]): Either[String, DataFrame] = {
  
  // Functional for-comprehension
  // Helper functions use `Either` to enable safe error handling
  for {
    baseDf <- tables.headOption.toRight("Pipeline requires at least one DataFrame")
    joinedDf <- applyJoins(baseDf, tables.tail, joinSpecs)
    result <- applyGrouping(joinedDf, groupByCols)
  } yield result
}
``` -->
```scala
// Safe, concise implementation
def buildDataPipeline(
  tables: Vector[DataFrame], 
  joinSpecs: Vector[JoinSpec], 
  groupByCols: Vector[String]
): Either[String, DataFrame] = {
  
  for {
    baseDf <- tables.headOption.toRight("Pipeline requires at least one DataFrame")
    _ <- Either.cond(tables.tail.length == joinSpecs.length, (), "Mismatch: tables and join specs")
    
    // Safe zip-based joining (no indexing needed)
    joinedDf = tables.tail.zip(joinSpecs).foldLeft(baseDf) { case (df, (joinDf, spec)) =>
      df.join(joinDf, col(spec.leftCol) === col(spec.rightCol), spec.joinType)
    }
    
    // Safe pattern matching for grouping
    result <- groupByCols match {
      case Vector() => 
        Right(joinedDf.agg(count("*").as("record_count")))
      case single +: rest => 
        val cols = (single +: rest).map(col)
        Right(joinedDf.groupBy(cols: _*).agg(count("*").as("count")))
    }
  } yield result
}

// Clean usage
buildDataPipeline(
  Vector(usersDf, ordersDf),
  Vector(JoinSpec("user_id", "user_id", "inner")),
  Vector("department", "status")
) match {
  case Left(error) => raise new RuntimeException(s"Pipeline failed due to invalid job spec: $error")
  case Right(df) => df.show()
}
```
I plan to write about functional for-comprehensions in a future post, as I find them an interesting topic as well!
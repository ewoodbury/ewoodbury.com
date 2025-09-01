---
title: "Safer Scala with WartRemover Part 1: Seq.apply and head"
date: 2025-08-25
draft: false
---

This is the first of a series of posts about using [WartRemover](https://www.wartremover.org/) to improve the quality of Scala codebases. WartRemover is a static analysis tool for Scala.

I find it a useful tool because it actively disables parts of Scala to improve safety. You get the benefits of a stricter language like Rust, while still being able to use `SuppressWarnings` as an escape hatch.

I also like that the warnings often present as a mini programming puzzle. Are you clever enough to fix it, maybe even without AI help?

---

Two closely-related Warts are `SeqIndex` and `Head`. These Warts ban the use of `Seq.apply` (i.e. indexing into a sequence with parentheses) and `Seq.head`, since both can throw exceptions at runtime.

Here's an example of real code from my [Sparklet](https://github.com/ewoodbury/sparklet) project that was caught by this Wart:

Before
```scala
private[execution] def materialize(ops: Vector[Operation]): Stage[Any, Any] = {

    return ops.head match { // WartRemover warning raised: .head is disabled
        case MapOp(f) => Stage.map(f.asInstanceOf[Any => Any])
        case FilterOp(p) => Stage.filter(p.asInstanceOf[Any => Boolean])
        case FlatMapOp(f) => Stage.flatMap(f.asInstanceOf[Any => IterableOnce[Any]])
        ...
```

After
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
The fix is simple for this case: check that the sequence is non-empty, and then use `headOption.get`, which is safe because of the prior check.


Similarly, here's an example of replacing `Seq.apply` with safe alternatives:

Before
```scala
    val shuffleInputSources = meta.kind match {
      case WideOpKind.Join | WideOpKind.CoGroup =>
        Seq(
          ShuffleInput(upstreamIds(0), Some(meta.sides(0)), meta.numPartitions), // simple indexing
          ShuffleInput(upstreamIds(1), Some(meta.sides(1)), meta.numPartitions)
        )
      case _ =>
        // Single-input operations
        require(upstreamIds.length == 1, s"${meta.kind} requires exactly 1 upstream stage")
        Seq(ShuffleInput(upstreamIds.head, None, meta.numPartitions)) // using head
    }
```
After
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

---

Of course, the `require` can still throw the exception for an emtpy sequence, but this fails fast and is easier to debug than a `NoSuchElementException`.

---

## Complex Example

The value is perhaps best demonstrated in a more complex case, where having WartRemover restrict `head` and `apply` forces a larger refactor, improving safety significantly.

Consider this Spark pipeline:

Before (unsafe, WartRemover warnings)
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

After (safe, functional approach)
```scala
import org.apache.spark.sql.{DataFrame, Column}
import org.apache.spark.sql.functions._

case class JoinSpec(leftCol: String, rightCol: String, joinType: String)

def buildDataPipeline(tables: Vector[DataFrame], 
                     joinSpecs: Vector[JoinSpec], 
                     groupByCols: Vector[String]): Either[String, DataFrame] = {
  
  // Function for-comprehension with automatic error handling
  for {
    baseDf <- tables.headOption.toRight("Pipeline requires at least one DataFrame")
    joinedDf <- applyJoins(baseDf, tables.tail, joinSpecs)
    result <- applyGrouping(joinedDf, groupByCols)
  } yield result
}

private def applyJoins(baseDf: DataFrame, joinDfs: Vector[DataFrame], 
                      joinSpecs: Vector[JoinSpec]): Either[String, DataFrame] = {
  if (joinDfs.length != joinSpecs.length) Left("DataFrame and join spec count mismatch")
  // Safe indexing with zip and fold
  else Right(joinDfs.zip(joinSpecs).foldLeft(baseDf) { case (df, (joinDf, spec)) =>
    df.join(joinDf, col(spec.leftCol) === col(spec.rightCol), spec.joinType)
  })
}

private def applyGrouping(df: DataFrame, groupByCols: Vector[String]): Either[String, DataFrame] = {
  groupByCols match {
    // Safe pattern matching instead of head/tail
    // Explicitly handle each case of empty, single, and multiple cols
    case Vector() => Right(df.agg(count("*").as("record_count")))
    case Vector(single) => Right(df.groupBy(col(single)).agg(count("*").as("record_count")))
    case primary +: rest => 
      val cols = (primary +: rest).map(col)
      Right(df.groupBy(cols.head, cols.tail: _*).agg(count("*").as("count"), sum(col(primary)).as("sum")))
  }
}

// Usage with safe error handling
val result = buildDataPipeline(
  tables = Vector(usersDf, ordersDf),
  joinSpecs = Vector(JoinSpec("user_id", "user_id", "inner")),
  groupByCols = Vector("department", "status")
)

result match {
  case Left(error) => println(s"Pipeline failed: $error")
  case Right(df) => df.show()
}
```

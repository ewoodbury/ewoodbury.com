## Spark: Stop using chained `withColumn` calls!

Chained `withColumn` calls are a common Spark pattern:

```scala
df.withColumn("newCol1", expr1)
  .withColumn("newCol2", expr2)
  .withColumn("newCol3", expr3)
```

First off, stop doing this! Even though it's readable
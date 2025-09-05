---
title: "Rebuilding Spark with Scala 3"
date: 2025-07-31
draft: false
---

Github Link: [Sparklet](https://github.com/ewoodbury/sparklet)

Over the last two years at Tesla, I've spent about 80% of my coding time in Spark. My team has moved a 50K-ish LOC data pipeline codebase from un-tested Python code to type-safe, fully-tested Scala Spark code. We've built about a dozen new, high-volume data pipelines in this project as well.

And...it's been fun! This was the first opportunity in years that I've been able to focus on code quality and architecture. I set out with the goal of building pipelines that are 100% correct over billion-row datasets and stable enough to run in factories for years to come, and my team has achieved that goal.

The experience has also sparked (wink) my interest in data processing internals. As a result, I've started a project to rebuild the Spark core in Scala 3.

## Current State

The project is in early stages, but the foundations are in place:

- Scala 3 for modern language features and best practices
- Planning of tasks and stages
- Lazy execution
- Basic user API
- Simulated cluster execution using local threads
- Effects system for task execution with cats-effect
- Full test coverage

My current goal is to finish implementing a full processing core, plus a DataFrame and DataSet API. From there, I'd like to run full data pipelines representative of a production Spark job.

## Why?

Of course, Spark isn't going anywhere.

But, it's still using Scala 2. Planning takes longer than it should. The web monitoring UI is a bit clunky and dated. There could be improvements in how query plans are displayed.

I'd like to build a proof of what a modern Spark could look like.

Selfishly, I want to gain experience building distributed systems and learning about how Spark really works.

## Alternatives

I'd be remiss not to mention the many other modern alternatives to Spark that already exist.

The most similar ones are those that maintain a focus on batch processing while support distributed execution out of the box. [Apache DataFusion](https://github.com/apache/datafusion) is fresh data engine in Rust, and [DataFusion Ballista](https://github.com/apache/datafusion-ballista) is the execution framework that enables writing actual jobs. [Ray](https://docs.ray.io/en/latest/data/data.html) is another distributed compute framework, although it's focused more on ML training workloads. Lastly, [Dask](https://github.com/dask/dask) is a mature Python framework for the same, although personally I've found it a bit clunky. 

(Edit 9/4): [Polars](https://github.com/pola-rs/polars), the company, [just launched](https://pola.rs/posts/polars-cloud-launch/) a distributed compute offering on AWS using the `polars` engine. I've enjoyed polars from my limited local usage, and it has a good reputation in the community, so I could see this gaining steam as well.

In the future, I'd like to explore contributing to Datafusion and Ballista, which I think have the most potential to grow into a full Spark competitor.

That all being said, I've been having a lot of fun with building and owning my own project end-to-end for now, and I hope to share more as it progresses. Check it out on [GitHub](https://github.com/ewoodbury/sparklet)!
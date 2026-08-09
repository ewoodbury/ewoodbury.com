---
title: "Safer Scala with WartRemover Part 3: Null and Option.get"
date: 2025-09-01
draft: true
---

This is the third post in a series about using WartRemover to improve Scala code quality, and more broadly about language safety.

## Nulls

Nulls (`None` for Pythonistas) are a common part of most programming languages, providing the escape hatch for unknown values such as API responses, or data inputs which can be missing.

However, type-safety requires an expression to preserve its type `T` through any allowed transformation, which improves program reliability by eliminating unexpected states. Nulls violate this constraint by the simple fact that nulls may cause a program which normally succeeds in returning a value with type `T`, to instead fail with a null-pointer exception. Practically, nulls are often defined far from where they are actually used, have little-to-no visible signature, and can quickly propagate everywhere causing every function to guard against them.

Hence the legendary Tony Hoare (from [Hoare logic](https://en.wikipedia.org/wiki/Hoare_logic)) called his invention of the null reference his ["billion-dollar mistake"](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/).

## Nulls In Scala

Much work has been put into handling nulls better across different programming languages. Scala in particular allows regular `Null` values, but it is discouraged. Scala 3 also added an opt-in feature for Explicit Nulls, which improves things by making reference types non-nullable by default, but it still leaves room for mistakes.

Common Scala guidance is to never use nulls within your own code, and to use `Option[T]` types instead. For Java interoperability, convert all nulls to `Option(javaApi.getObject())` at the boundary.

```scala
def findUser(id: Int): Option[User] = ...

findUser(42) match {
  case Some(user) => user.name
  case None => "unknown"
}

// or:
findUser(42).map(_.name).get
```

The beauty of this approach, and of banning all nulls via WartRemover, is that nulls can no longer exist as umbrella types at all. We can rule out all bugs due to a normal-looking type hiding a null value. All missing values are now expressed in the first-class types, which means the Scala compiler now forces you to handle them.

For cases where the missing value should cause the program to fail visibly, use `Either[E, T]` instead:

```scala
def findUser(id: Int): Either[String, User] = ...

findUser(42) match {
  case Right(user) => user.name
  case Left(err)   => s"failed: $err"
}
// or using fold:
findUser(42).fold(
  err  => s"failed: $err",
  user => user.name
)
```

In a similar vein, we need to ban raw `.get` calls for the same reason, that it could be used to unwrap an `Option` variable which could either succeed or crash. Instead we use `getOrElse()`, so we're forced to provide a default value for the missing case.

If you have a sharp eye, you noticed the unsafe `.get` call above; the fixed version is:
```scala
findUser(42).map(_.name).getOrElse("unknown")
```

If the missing value is a failure using `Either`, the alternative here for `.get` would be `toRight`:
```scala
findUser(42).toRight("User not found")
```


## Full Example

We show the value of banning nulls in a slightly larger program here, with a naive approach:

```scala
def welcomeEmail(
  userId: String,
  users: Map[String, User],
  prefs: Map[String, String]
): String = {
  val user = users.get(userId).getOrElse(null)
  if (user == null) return null

  val email = user.email // Java-nullable String
  if (email == null) throw new RuntimeException(s"$userId has no email")

  val name    = Option(user.name).getOrElse("there")
  val locale  = prefs.get("locale").getOrElse(null)
  val subject = prefs.get("subject").get

  if (locale == null) s"$subject\nHi $name <$email>"
  else s"$subject\nHi $name <$email> ($locale)"
}
```
Not only are there ugly null guards sprinkled throughout the code; the entire function return type lies since it can return null in its entirety. It's silly this compiles at all!

Here's the cleaned up snippet conforming to the WartRemover rules:

```scala
final case class WelcomeEmail(
  subject: String,
  name: String,
  email: String,
  locale: Option[String]
)

def welcomeEmail(
  userId: String,
  users: Map[String, User],
  prefs: Map[String, String]
): Either[String, WelcomeEmail] =
  for {
    user    <- users.get(userId).toRight(s"unknown user $userId")
    email   <- Option(user.email).toRight(s"$userId has no email")
    subject <- prefs.get("subject").toRight("missing subject")
  } yield WelcomeEmail(
    subject = subject,
    name    = Option(user.name).getOrElse("there"), // real default
    email   = email,
    locale  = prefs.get("locale")                   // stays optional
  )
```

## WartRemover

For completeness, to set these rules simply set in your build.sbt:
```scala
wartremoverErrors ++= Seq(
  Wart.Null,
  Wart.OptionPartial
)
```

Scala still needs to deal with nulls from libraries and Java interoperability, so this isn't quite as complete as Haskell or Rust where nulls are fully nonexistent. Still, WartRemover gets Scala as close as you can get to these strict languages, within the JVM ecosystem.

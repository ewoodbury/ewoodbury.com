---
title: "Navier Stokes: A Gentle Introduction"
date: 2026-09-12
draft: true
---

It's been a big week for the world of AI + Math. 

In a past life, I studied Chemical Engineering, which is really just a field of Applied Math. My degree was particularly focused on theory, so I spent a huge fraction of my life working out differential equations governing fluid flow and other many other physical phenomena. So,

Much has been said about the changing landscape of math research in a post-AI world. For this occasion though, the propasl of a Millenium Prize solution should be celebrated, especially with it being the problem with the most connection to the physical world. I took the opportunity to refamiliarize myself with this math of Navier Stokes, and to put together an approachable introduction for folks who want to build some understanding. It should be accessible to anyone with basics introductory physics and basic algebra, although familiarity with calculus is a big help too.

This post is only a simple, non-rigorous introductions to the Navier Stokes equations themselves; I don't cover the contributions of Buckmaster/Alpoge or OpenAI here yet.

---

Fluid dynamics is the study of forces on a continuous mass (liquids and gasses), in contrast to rigid body dynamics. In that sense, one could think of fluid dynamics as extending the typical dynamics concepts from Physics 1 (`F = ma`, `\(\tau = r \times F \times \sin(\theta)\),`) onto a body of infinitesimally small objects, until you reach the point of modeling the forces on a single continuous, flowing mass. It's a somewhat similar idea of going for discrete variables in algebra to continuous quantities and limits in calculus, an idea many more have grappled with in high school math. (Of course this is an extreme oversimplification, but it helps frame the question of "what is fluid dynamics" and explains how we came up with this new set of equations.)

## Mass Balance

Before we get to the full equations, the key concept to be familiar with is that of the physical laws of conservation. It's obvious that mass is conserved (ignoring relativity), whether dealing with discrete objects or our continuous case with fluids. Mass inside a closed system is conserved, because nothing can flow in or out. In an open system though, we can describe the change in mass simply by writing a "balance", which simply accounts for what flows in versus what flow out. (Note I'm starting by assuming an incompressible fluid, e.g. water).

In words, for a given volume, our mass balance is simply: `( net inflow )  +  ( net outflow )  =  0`. In math, it's simple `∇·u = 0`, where `u` is what we use for mass, and `∇` is the gradient operator and essentially means the total change in mass across all 3 dimensions. 

```
Mass Balance (Incompressible fluid)

∇·u = 0
```

This is very intuitive: if you stick a straw in a flowing stream, the amount of water in it is always constant, as the volume of water flowing in is exactly equal to the volume flow out.

Now, if instead of water, what if we're dealing with air, which is compressible? If you hold a straw in a stream of air, and a large gust blows through it, then for an instant there is more mass of air in the straw. To account for this, we add a density term to the equation. The mass balance still holds; no mass is created or destroyed. The balance now tracks the change of mass over time inside the volume. Since we're keeping a constant control volume, we divide by the volume to track change in density (`rho`) instead:

```
Mass Balance (Compressible Fluid)
∂ρ/∂t          +   ∇·(ρu)         =   0
```

Here, the dp/dt term is the math expression for change (d) in density (rho) over time (t). The gradient (∇) term is also modified with a rho term to account for the possible density difference of flow in versus out. Then, the zero is unchanged to reflect conservation of mass.

Annotated, this is: 
```
∂ρ/∂t          +   ∇·(ρu)         =   0
(change inside)    (carried by        (no way to
                    the flow)          create it)
```


## Momentum Balance

The other conservation quantity is momentum: we construct a similar momentum balance to track the effect of forces on the fluid's properties. 

Recall that momentum is `mass * velocity`, yet we divide by the a constant volume to track in terms of density instead. So we'll make the balance on the momentum term `pu`.

For inflows and outflows, we again track the changes at the edge of the container. Here that term is `∇·(ρu ⊗ u)` (the `⊗` is a cross-product; essentially a multiplication in 3D space).

The last term accounts for the change in momentum from forces. Unlike mass however, momentum can be created or destroyed. Yet we track that momentum is conserved via forces: any change in momentum must always be accompanied with an applied force.


∂u/∂t + (u·∇)u  =  −(1/ρ)∇p  +  b



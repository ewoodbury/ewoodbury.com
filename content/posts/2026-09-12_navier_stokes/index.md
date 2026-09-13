---
title: "Navier Stokes: A Gentle Introduction"
date: 2026-09-12
draft: true
---

My academic background was in Chemical Engineering, so it was particularly exciting for me to see the Navier-Stokes equations, something which I spent a meaningful fraction of my life studying, suddenly becoming front page news and fuel the weekly controversy across the global town square of X.

Across the many conversations and viewpoints though, one piece that I don't want to be missed is the meaningfulness of a Millenium Prize solution, especially with it being the problem with the most connection to the physical world. This is the one Millenium problem that a person with light math background has a chance to fully understand, at least for the raw equations themselves. I took the opportunity to refamiliarize myself with this math of Navier Stokes, and to put together an approachable introduction for folks who want to build some understanding. It should be accessible to anyone with basics introductory physics and basic algebra, although familiarity with calculus is a big help too.

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

For inflows and outflows, we again track the changes at the edge of the container. Here that term is `(u·∇)u `.

The last term accounts for the change in momentum from forces. Unlike mass however, momentum can be created: we track that momentum is conserved via forces: any change in momentum must always be accompanied with an applied force (from Newton's 2nd Law and `F = ma`).

For fluids, the momentum from external forces is split into two terms. The first is body forces, and expressed as `rho*b`. Again rho is the mass term, and b is the simply the force per unit mass, which we can typically take as gravity (9.8 m/s^2). This term is exactly the same as for a rigid body (F_gravity = mg) as fluid acts the same on both.

The second term is due to pressure in the fluid. A fluid is fully made up of particles constantly colliding with each other, exerting a force with each collision. With Newton's 3rd law we know that every force has an equal and opposite reaction, which has the nice effect of cancelling out in pairs. The only forces not cancelled are those at the edge of the volume: forces coming from outside of the control volume. We can simply express this as `∇p`. Simply having high versus low pressure doesn't make a difference; it's the net force due to the difference in pressures on different sides of the volume.

At this point, we can put this all together as:
```
Euler Momentum balance

∂(ρu)/∂t       +   ∇·(ρu ⊗ u)     =   −∇p + ρb
(change inside)    (carried by        (created by
                    the flow)          forces)
```

In words, the momentum change inside the volume plus the momentum change from inflows and outflows, must always equal the net forces exerted on the volume.

Therefore, we have analogous balances for both mass and momentum now, all descending from the basic laws of physics. These are the basic building blocks from which Navier Stokes is built.

### Notes

At this point, we've already arrived at an incredibly useful governing equation for both applications with low viscosity fluids (airflow, weather, flow through pipes) and for setting a foundation for mathematical explorations. In fact, this was the equation attacked by the team of Buckmaster + Alpoge in their recent research.

Next, we'll add in viscosity -- that is shear forces of the fluid upon itself, such as in honey.

## Generalizing Momentum with Shear Forces

Now, note that pressure is the common way of thinking about forces in fluids; the outside pressure is always pointed inward. In a more general sense, there can be sideways and diagonal forces on a volume of fluid. We use `sigma` for this tensor force instead of pressure `P`.


In practical terms, σ is a field dependent on the pressure: water at 1m depth is at ~1.1 atm of pressure, so:
```
       [ −1.1×10⁵      0          0    ]
σ  ≈   [    0      −1.1×10⁵       0    ]  Pa
       [    0          0      −1.1×10⁵ ]
```

If pressure doubles, those values double as well. But the non-diagonal terms which represent the shear forces are zero here: this means we assume there is no sideways forces within the fluid and the viscosity is zero. Think about putting a layer of water between two flat baking pans and sliding them past each other; there is essentially no resistance.

But what if that were a layer of honey instead: now there is significant resistance to sliding the two pans. This is because honey has viscosity: it conducts the sheer forces within itself and thus resists a change in momentum even when under the same force.

In this case, with a hypothetical pool of honey at 1m deep, our sigma terrm might instead be:

```
       [ −1.1×10⁵      −0.5×10⁵      −0.5×10⁵    ]
σ  ≈   [ −0.5×10⁵      −1.1×10⁵      −0.5×10⁵    ]  Pa
       [ −0.5×10⁵      −0.5×10⁵      −1.1×10⁵    ]
```

With this generalization of shear force included, we arrive at the full Cauchy momentum balance:
```
Cauchy Momentum Equation

∂(ρu)/∂t + ∇·(ρu⊗u)  =  ∇·σ + ρb
```

As an additional step, we can consolidate the inflow/outflow gradient term to be inside the derivative.

```
ρ [ ∂u/∂t + (u·∇)u ] = ∇·σ + ρb

simplifies to the simplified Cauchy equation:

ρ Du/Dt = ∇·σ + ρb
```

## Expanding on Viscous Stress to get Navier-Stokes

We already saw that in the no-viscosity case, `σ` was simple set as pressure `P`, and with the full Cauchy, `σ` does include the additional stress terms.

More formally math, this can be shown as:
```
σ = −pI  +  σᵛ

where `I` is the identity matrix
[ 1 0 0 ]
[ 0 1 0 ]
[ 0 0 1 ], 
and σᵛ is the term for the viscous forces only.
```
However, note that the viscous forces are not only off-diagonal; they are a full tensor force in all three dimentions and `σᵛ` is fully nonzero. For compressible fluids, the forces can literally compress the fluid by pushing inward, in the same direction as regular pressure forces.

Next up though, we break down `σᵛ` into smaller terms that inform the forces actually involved. We do so as:
```
σᵛ  =  (some tensor constant) × (rate of deformation)
```
The tensor constant is the physical property, it only depends on what the fluid is that we're working with. Water has low viscosity while honey has high, so that tensor constant is higher for honey and it transfers more momentum across the fluid body for a given force.

The rate of deformation is also intuitive: the faster you slide the two pans across the liquid, the greater the force.
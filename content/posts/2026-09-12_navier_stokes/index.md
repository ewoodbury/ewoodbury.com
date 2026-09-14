---
title: "Navier Stokes: A Gentle Introduction"
date: 2026-09-12
draft: true
---

My academic background was in Chemical Engineering, so it was particularly exciting for me to see the Navier-Stokes equations, something I spent a meaningful fraction of my life studying, suddenly becoming front page news and fueling the weekly controversy on X.

Despite the controversy, one thing which shouldn't be missed is we know the solution to another Millenium Prize solution! Particularly so, with Navier-Stokes being the problem with the most connection to the physical world. This is the one Millenium problem that a person with light math background has a chance to fully understand, at least for the raw equations themselves. I took the opportunity to refamiliarize myself with this math, and to put together an approachable introduction for anyone wanting to build an intuitive understanding. 

I wrote this to be accessible to anyone with basics physics and algebra knowledge, as it grounds the entire equation in physical intuition. I includ the full mathematical contex too, but you should be able to skim this and still understand the equations fully. To grasp the math, you'll need some understanding of partial differential equations, gradient and divergence, and basic linear algebra (basic matrix math).

This post on covers the Navier Stokes equations themselves; I don't cover the contributions of Buckmaster/Alpoge or OpenAI here yet.

---

Fluid dynamics is the study of forces on a continuous mass (liquids and gasses), in contrast to rigid body dynamics. In that sense, one could think of fluid dynamics as extending the typical dynamics concepts from Physics 1 (`F = ma`, `\(\tau = r \times F \times \sin(\theta)\),`) onto a body of infinitesimally small objects, until you reach the point of modeling the forces on a single continuous, flowing mass. It's similar to going from algebra to calculus, where we go from discrete variables to continuous quantities at tiny scales (This is of course an oversimplification, but it helps frame the question of "what is fluid dynamics" and explains how we came up with this new set of equations.)

## Mass Balance

Before we get to the full equations, the key concept to be familiar with is that of the physical laws of conservation. It's obvious that mass is conserved (ignoring relativity), whether dealing with discrete objects or our continuous case with fluids. Mass inside a closed system is conserved, because nothing can flow in or out. In an open system though, we can describe the change in mass simply by writing a "balance", which simply accounts for what flows in versus what flow out. (Note I'm starting by assuming an incompressible fluid, e.g. water).

In words, for a given volume, our mass balance is simply: `( net inflow )  +  ( net outflow )  =  0`. In math, it's simple `∇·u = 0`, where `u` is what we use for mass, and `∇·` is the divergence operator and essentially means the total outward change in mass, summed across all 3 dimensions. 

```
Mass Balance (Incompressible fluid)

∇·u = 0
```

This is intuitive: if you hold a straw in a flowing stream, the amount of water in it is always constant, as the volume of water flowing in is exactly equal to the volume flow out.

Now, if instead of water, what if we're dealing with air, which is compressible? If you hold a straw in a stream of air, and a large gust blows through it, then for an instant there is more mass of air in the straw. We account for this by adding a density term. The mass balance still holds since no mass is created or destroyed; it just now tracks the change of mass over time inside the volume. Since we're keeping a constant control volume, we divide by the volume to track change in density (`rho`) instead:

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


## Momentum Balance (Euler Equation)

The other conservation quantity is momentum: we construct a similar momentum balance to track the effect of forces on the fluid's properties. 

Recall that momentum is `mass * velocity`, yet we divide by the a constant volume to track in terms of density instead. So we'll make the balance on the momentum term `pu`.

For inflows and outflows, we again track the changes at the edge of the container. Here that term is `(u·∇)u`.

The last term accounts for the change in momentum from forces. Unlike mass however, momentum can be created: we track that momentum is conserved via forces: any change in momentum must always be accompanied with an applied force (from Newton's 2nd Law and `F = ma`).

For fluids, the momentum from external forces is split into two terms. The first is body forces, and expressed as `rho*b`. `rho` is still density, and b is the simply the force per unit mass, which we can typically take as gravity (9.8 m/s^2). This term is exactly the same as for a rigid body (`F_gravity = mg`) since gravity acts the same on both.

The second term is pressure in the fluid. A fluid is fully made up of particles constantly colliding with each other, with each collision exerting a force. From Newton's 3rd law, every force has an equal and opposite reaction, so all collisions cancel out forces in pair. The only forces not cancelled are those at the edges, from forces coming from outside of the control volume. 

We simply express the net force as `∇p`, where `∇` (without the dot) is the gradient operator and means the change in all 3 dimensions. Simply having high versus low pressure doesn't make a difference; it's the net force due to the difference in pressures on different sides of the volume.

At this point, we can put it together the full momentum balance:
```
Euler Momentum balance

∂(ρu)/∂t       +   ∇·(ρu ⊗ u)     =   −∇p + ρb
(change inside)    (carried by        (created by
                    the flow)          forces)
```

In words, the momentum change inside the volume plus the momentum change from inflows and outflows, must always equal the net forces exerted on the volume.

Therefore, we have analogous balances for both mass and momentum now, all descending from the basic laws of physics. These are the basic building blocks from which Navier Stokes is built.

At this point, we've already arrived at an incredibly useful governing equation for both applications with low viscosity fluids (airflow, weather, flow through pipes) and for setting a foundation for mathematical explorations. In fact, this was the equation attacked by the team of Buckmaster + Alpoge in their recent research.

Next, we'll add in viscosity, which is shear (dragging) force of the fluid upon itself, such as in when spreading honey.

## Shear Forces (Cauchy momentum)

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

## Final Steps to Navier-Stokes

### Viscous Forces

We already saw that in the no-viscosity case, `σ` was simple set as pressure `P`, and with the full Cauchy, `σ` does include the additional stress terms.

In math, this can be shown as:
```
σ = −pI  +  σᵛ
```
where `I` is the identity matrix (think of it of multiplying by 1 but in 3D), and σᵛ is the term for the viscous forces only.


Next up though, we break down `σᵛ` into smaller terms that inform the forces actually involved. We do so as:
```
σᵛ  =  (some tensor constant) × (rate of deformation)
```
The tensor constant is the physical property, it only depends on what the fluid is that we're working with. Water has low viscosity while honey has high, so that tensor constant is higher for honey and it transfers more momentum across the fluid body for a given force.

The rate of deformation is also intuitive: the faster you slide the two pans across the liquid, the greater the force. Let's further break down this rate term.
```
σᵛ = 2μE      +       λ(∇·u) I
     ↑                   ↑
   resists SHEARING      resists EXPANSION/compression
   (shear viscosity μ)   (bulk viscosity λ)
```
As mentioned above, this consists of pure shear forces (side-to-side) and pressure forces (in and out), each of which has their own viscosity constant per fluid: `μ` as the shear viscosity, and `λ` as the build viscosity. Again, shear is the sliding force: water versus honey. Bulk viscosity is a bit harder to visualize, but it's essentially how hard the fluid is to squeeze. A balloon full of air can be squeezed to reduce volume pretty easily; a water balloon on the other hand does not compress, any squeezes will just move water around, with overall balloon volume remaining constant.

Then, `E` and `(∇·u)` are simply the deformation rates. Faster sliding means higher E, and faster compression/expansion means higher magnitude of `(∇·u)`. More explicitly, to break down to simplest terms, E can be given as:
```
E = ½(∇u + ∇uᵀ)
```
to be in terms of the same velocity gradient `∇u` and the antisymmetric term `∇uᵀ` (from matrix algebra).

Therefore, we arrive at:

```
σᵛ  =  2μE  +  λ(∇·u) I =  μ(∇u + ∇uᵀ)  +  λ(∇·u)
```

### Putting it all Together

At this point, it's a pure algebra exercise, with the goal of simplifying everything down to the basic variables of density `rho`, velocity `u`, and constants.

First we take our new shear viscosity term `σᵛ` and apply the divergence operator, since that's where Cauchy has the `σ`:
```
∇·σᵛ = μ∇²u + μ∇(∇·u) + λ∇(∇·u)
```


```
ρ Du/Dt = ∇·σ + ρb

-->

ρ Du/Dt = ∇·(−pI  +  σᵛ) + ρb

-->

ρ Du/Dt = −∇p + μ∇²u + (λ + μ)∇(∇·u) + ρb
```

And that's it! We've now arrived at the full Navier-Stokes equation governing fluid flow, all in terms of basic, measurable fluid properties.

```
Full Navier-Stokes (compressible fluid)
ρ Du/Dt = −∇p + μ∇²u + (λ + μ)∇(∇·u) + ρb
```

We've touched on the simplifications across this derivation, but to show them together here as they'll often be applied to show as a simplified form:
```
Euler:              σᵛ = 0                  (no viscous at all)
ρ Du/Dt = ∇·σ + ρb

Incompressible NS:  σᵛ = 2μE                (λ-term dead: ∇·u = 0)
ρ Du/Dt = −∇p + μ∇²u + μ∇(∇·u)
```

## The 2026 Proposed Solution

Although I won't deeply analyze the Millenium Prize problem and solution itself, I do think it's worth a passing discussion after we walked through the full derivation.

The problem essentially asks the question: does Navier-Stokes hold up across all time-scales and length-scales, or does it break down under some sort special conditions? In other words, do these equations result in an impossible infinite fluid velocity under some physical conditions?

There were two dimensions of the problem under active research: without vs. with viscous forces (Euler equation vs. full N-S), with the Buckmaster/Alpoge tackling Euler and OAI tacking full N-S. Second dimension is forced versus unforced, where forced means some external force is applied to the system to cause a perturbation in the fluid and cause the breakdown, and unforced goes without any external perturbation. I'm not familiar with the active research, but both Buckmaster/Alpoge and OAI tackled the forced setup, while unforced seemed to be the much more common current research area, and this fact was the major driver of the research privacy controversy.

Of course, it shouldn't be overlooked that any version of these solutions is a massive milestone for fluid dynamics and mathematics overall. I hope that this can be a spark for further mathematics research into related and new problems, and that it can be an opportunity for the wider world to get some insight and I dare say even enjoyment into this typically inaccessible field.

## Wrap-up

In my opinion this is an elegant derivation, in that it does not depend on any esoteric concepts, mathematical constructions, or 4+ dimensional systems. Every single term has a true physical analogue that anyone could visualize. Yet despite the simplicity, it builds a governing equation that can be the subject of study of both engineering and pure math for hundreds of years. It also feels stunning to me that only in 2026, have we found the true limits of where this equation can be applied.

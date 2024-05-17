### The decision model

##What is in the model
We let $G = \{g_1,\dots,g_{|G|}\}$ be the set of possible gowns.
We discretize time into time-frames, collected in the set $T$. Let's take $|T|=150$, which should equal roughly a year. We index $T=\{t_1,\dots,t_{|T|}\}$.

##Decision variables
As this is a procurement tool, the core decision variables are regarding the procurement of gowns.
For each time-frame and gown, with $z(x,t)$ whether or not we have a new arrival of said gown in that time-frame. BINARY-valued.
How many new gowns arrive, is indexed by $b(x,t)$ for $x \in G, t \in T$. INTEGER-valued.


##Flow variables
There are some auxiliary variables that manage the flow. They have limited freedom.
All following variables are index per type of gown, per time-step:

The variables $h(x,t)$ indicate how many gowns at the Hospital. INTEGER-valued.
The variables $w(x,t)$ indicate how many gowns at the Laundry. INTEGER-valued.
The variables $u(x,t)$ indicate how many gowns are used at the Hospital. INTEGER-valued.
The variables $ls(x,t)$ indicate how many gowns got lost between time $t-1$ and $t$. INTEGER-valued.
The variables $lf(x,t)$ indicate how many gowns are going to the End-of-Life-cyclus. INTEGER-valued.

To keep track of arriving gowns, we have the following set of constraints:
$$
b(x,t) <= M \cdot z(x,t)
$$
Where $M$ is a very large (arbitrary) number. This constraints makes sure that only when $z(x,t) = 1$, $b(x,t)$ can be non-zero, while not limiting the number of new gowns of type $x$ that can arrive at time $t$.

To manage the flow, we have the following set of constraints:
$$
h(x,t) = h(x,t-1) - u(x,t-1) + b(x,t-1) + w(x,t-1) \\
u(x,t-1) = w(x,t) + ls(x,t) + lf(x,t) \\
w(x,t) <= c_x \cdot h(x,t-1)
$$
Where $0 <= c_x <= 1$ is a coefficient that is $0$ when a gown in single-use, and $1$ otherwise.

##Parameter impacts
There is an encyclopedia $E$ containing all relevant impacts for gowns regarding the environment and the use-phase. For each gown $x$, parameter $P$ and use-phase $U$ we have an entry $E(x,P,U)$. For each parameter $P$ we have the total impact of the schedule as:
$$C(P) = \sum_{U}\sum_{x,t}U(x,t) \cdot E(x,P,U)$$ 
where $U \in \{h,w,u,ls,lf,b\} - all functions we created earlier (this is extremely ugly notation, we can do better). 
Parameters are for example: 
- CO2-equivalence
- MJ-energy usage
- Water usage
- Costs

##Objectives






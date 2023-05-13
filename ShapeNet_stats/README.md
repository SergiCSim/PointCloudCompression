``get_info()`` function from ``pointclouds.py`` calculates some information and stats from a point cloud. With the ``extract_stats.py`` script, the stats from an entire dataset can be extracted and are stored in some csv files, where each row has the information of one of the point clouds of the dataset. The first column from these csv files, **File name**, is the name of the file where the points of the point cloud are stored. The next columns are the information and stats extracted using ```get_info()```. They are:

**Range x,Range y,Range z,Bit depth,Prop. empty sl. x,Prop. empty sl. y,Prop. empty sl. z,Ocup. voxels x (min),Ocup. voxels x (max),Ocup. voxels x (mean),Ocup. voxels x (median),Ocup. voxels y (min),Ocup. voxels y (max),Ocup. voxels y (mean),Ocup. voxels y (median),Ocup. voxels z (min),Ocup. voxels z (max),Ocup. voxels z (mean),Ocup. voxels z (median),Bottom hor. x (min),Bottom hor. x (max),Bottom hor. x (mean),Bottom hor. x (median),Bottom hor. y (min),Bottom hor. y (max),Bottom hor. y (mean),Bottom hor. y (median),Bottom hor. z (min),Bottom hor. z (max),Bottom hor. z (mean),Bottom hor. z (median),Bottom vert. x (min),Bottom vert. x (max),Bottom vert. x (mean),Bottom vert. x (median),Bottom vert. y (min),Bottom vert. y (max),Bottom vert. y (mean),Bottom vert. y (median),Bottom vert. z (min),Bottom vert. z (max),Bottom vert. z (mean),Bottom vert. z (median),Top  hor. x (min),Top  hor. x (max),Top  hor. x (mean),Top  hor. x (median),Top  hor. y (min),Top  hor. y (max),Top  hor. y (mean),Top  hor. y (median),Top  hor. z (min),Top  hor. z (max),Top  hor. z (mean),Top  hor. z (median),Top vert. x (min),Top vert. x (max),Top vert. x (mean),Top vert. x (median),Top vert. y (min),Top vert. y (max),Top vert. y (mean),Top vert. y (median),Top vert. z (min),Top vert. z (max),Top vert. z (mean),Top vert. z (median),Entropy x (min),Entropy x (max),Entropy x (mean),Entropy y (min),Entropy y (max),Entropy y (mean),Entropy z (min),Entropy z (max),Entropy z (mean),SR entropy x (min),SR entropy x (max),SR entropy x (mean),SR entropy y (min),SR entropy y (max),SR entropy y (mean),SR entropy z (min),SR entropy z (max),SR entropy z (mean)**

Before explaining what each column means, some concepts and definitions need to be explained.

A preprocessed point cloud can be represented as a set of $N$ points

$$
P = \{ (x_n, y_n, z_n) \in \mathbb{N_0^3} \}_{n=1, \dots, N},
$$

and, for each axis,
$$
X = \{ x_n\}_{n=1, \dots, N}
$$
$$
Y = \{ y_n\}_{n=1, \dots, N}
$$
$$
Z = \{ z_n\}_{n=1, \dots, N}
$$

We can also define mathematically the $i$-th slice across the x axis, for $i=1, \dots, \operatorname{max} X$ as

$$
S_x^{(i)} = \{ (x_n, y_n, z_n) \in P : x_n = i \}_{n=1, \dots, N}
$$

 the $j$-th slice across the y axis, for $j=1, \dots, \operatorname{max} Y$ as

$$
S_y^{(j)} = \{ (x_n, y_n, z_n) \in P : y_n = j \}_{n=1, \dots, N}
$$

and the $k$-th slice across the z axis, for $k=1, \dots, \operatorname{max} Z$ as

$$
S_z^{(k)} = \{ (x_n, y_n, z_n) \in P : z_n = k \}_{n=1, \dots, N}.
$$

### Ranges:

For each axis, its range is its maximum value. That is:

* **Range x:**
$$
\operatorname{max} X
$$

* **Range y:**
$$
\operatorname{max} Y
$$

* **Range z:**
$$
\operatorname{max} Z
$$

### Bit depth

The bit depth is a unique value which represents the minimum number of bits needed to represent each value of the point cloud. Mathematically:

* **Bit depth:** 
$$
\lfloor 1 + \log_2 \operatorname{max} \{\operatorname{max} X, \operatorname{max} Y, \operatorname{max} Z \} \rfloor
$$

###  Proportions of empty slices:

The proportion of empty slices, for each axis, is the number of slices across this axis with no points divided by the total number of slices. Or, in other words, one minus the proportion of slices with, at least, one point.

* **Prop. empty sl. x:**
$$
1 - \frac{\# \{ S_x^{(i)} : \# S_x^{(i)} > 0\}}{\operatorname{max} X}
$$

* **Prop. empty sl. y:**
$$
1 - \frac{\# \{ S_y^{(j)} : \# S_y^{(j)} > 0\}}{\operatorname{max} Y}
$$

* **Prop. empty sl. z:**
$$
1 - \frac{\# \{ S_z^{(k)} : \# S_z^{(k)} > 0\}}{\operatorname{max} Z}
$$

### Number of occupied voxels

The number of occupied voxels in a slice is the number of voxels that represent a point of the point cloud in this slice.

* **Ocup. voxels x** for each slice $i=1, \dots, \operatorname{max} X$ across the x axis:

$$
\# S_x^{(i)}
$$

* **Ocup. voxels y** for each slice $j=1, \dots, \operatorname{max} Y$ across the y axis:

$$
\# S_y^{(j)}
$$

* **Ocup. voxels z** for each slice $k=1, \dots, \operatorname{max} Z$ across the z axis:

$$
\# S_z^{(k)}
$$

Instead of having all the values of occupied voxels from each axis and slice, there is the **min**, the **max**, the **mean** and the **median** of every slice for each axis.

### Signalling rectangles

The signalling rectangle of one slice is the rectangle with the minimum area that contains all the points of that slice.

Each signalling rectangle can be represented by two points, the top right point and the bottom left point. The top right point for the $i$-th slice across the x axis can be denoted as $(y_{tr}^{(i)}, z_{tr}^{(i)})$, and the bottom left as $(y_{bl}^{(i)}, z_{bl}^{(i)})$; $(x_{tr}^{(j)}, z_{tr}^{(j)})$ and $(x_{bl}^{(j)}, z_{bl}^{(j)})$ for the y axis, and $(x_{tr}^{(k)}, y_{tr}^{(k)})$ and $(x_{bl}^{(k)}, y_{bl}^{(k)})$ for the z axis.

The calculated values are:

* **(Bottom hor. x, Bottom vert. x)** for each slice $i=1, \dots, \operatorname{max} X$ across the x axis:

$$
(y_{bl}^{(i)}, z_{bl}^{(i)})
$$

* **(Bottom hor. y, Bottom vert. y)** for each slice $j=1, \dots, \operatorname{max} Y$ across the y axis:

$$
(x_{bl}^{(j)}, z_{bl}^{(j)})
$$

* **(Bottom hor. z, Bottom vert. z)** for each slice $k=1, \dots, \operatorname{max} Z$ across the z axis:
$$
(x_{bl}^{(k)}, y_{bl}^{(k)})
$$

* **(Top hor. x, Top vert. x)** for each slice $i=1, \dots, \operatorname{max} X$ across the x axis:

$$
(y_{tr}^{(i)}, z_{tr}^{(i)})
$$

* **(Top hor. y, Top vert. y)** for each slice $j=1, \dots, \operatorname{max} Y$ across the y axis:

$$
(x_{tr}^{(j)}, z_{tr}^{(j)})
$$

* **(Top hor. z, Top vert. z)** for each slice $k=1, \dots, \operatorname{max} Z$ across the z axis:
$$
(x_{tr}^{(k)}, y_{tr}^{(k)})
$$

Instead of having all the values of the components of the signalling rectangle points from each axis and slice, there is the **min**, the **max**, the **mean** and the **median** of each of them.
### Binary entropies

The binary entropy of $N$ bits $b_1, b_2, \dots, b_N$ is defined as

$$
H_b(p) = p \log_2 \frac{1}{p} + (1-p) \log_2 \frac{1}{1-p},
$$

where

$$
p=\frac{1}{n} \displaystyle \sum_{n=1}^{N} b_n,
$$

and it gets its maximum value when $p=\frac{1}{2}$, that is, when the number of $0$ bits is the same as the number of $1$ bits.

In our case, in one slice we consider that a voxel has the value $0$ when it is empty and $1$ when it represents a point. So, for example, the binary entropy of the first slice across the x axis will be $H_b(p_1)$, where $p_1$ will be the proportion of occupied voxels in this slice.

So, mathematically:

* **Entropy x** for each slice $i=1, \dots, \operatorname{max} X$ across the x axis:

$$
H_b(p_i), p_i = \frac{\# S_x^{(i)}}{\operatorname{max} Y \operatorname{max} Z}
$$

* **Entropy y** for each slice $j=1, \dots, \operatorname{max} Y$ across the y axis:

$$
H_b(p_j), p_j = \frac{\# S_y^{(j)}}{\operatorname{max} X \operatorname{max} Z}
$$

* **Entropy z** for each slice $k=1, \dots, \operatorname{max} Z$ across the z axis:

$$
H_b(p_k), p_k = \frac{\# S_z^{(k)}}{\operatorname{max} X \operatorname{max} Y}
$$

The entropy of each slice across each axis is also calculated but considering only the voxels of the signalling rectangle, so the probabilities are different: they are calculated by dividing by the width multiplied by the height of each signalling rectangle. The width of the rectangle of the $i$-th slice can be noted as $w_x^{(i)}$, and the height as $h_x^{(i)}$, and the same for the y and z axis.

So, the second entropies are:

* **SR entropy x** for each slice $i=1, \dots, \operatorname{max} X$ across the x axis:

$$
H_b(p_i), p_i = \frac{\# S_x^{(i)}}{w_x^{(i)} h_x^{(i)}}
$$

* **SR entropy y** for each slice $j=1, \dots, \operatorname{max} Y$ across the y axis:

$$
H_b(p_j), p_j = \frac{\# S_y^{(j)}}{w_y^{(j)} h_y^{(j)}}
$$

* **SR entropy z** for each slice $k=1, \dots, \operatorname{max} Z$ across the z axis:

$$
H_b(p_k), p_k = \frac{\# S_z^{(k)}}{w_z^{(k)} h_z^{(k)}}
$$

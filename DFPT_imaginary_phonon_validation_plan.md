# Nb₂Pd₃Te₅ Γ 点 DFPT 假虚频：验证与定位实验计划

更新日期：2026-09-17

## 0. 研究目标

当前 Nb₂Pd₃Te₅ 的 Γ 点 `A_g` 模存在明显的 DFPT–有限位移矛盾：

- 有限位移能量曲率：`K_E ≈ +24.9147 eV/Å²`
- 有限位移力曲率：`K_F ≈ +24.9051 eV/Å²`
- QE `ph.x` DFPT 投影曲率：`K_DFPT ≈ -104.8938 eV/Å²`

因此当前最重要的问题已经不是“这个结构是否真的不稳定”，而是：

> **为什么 QE 的线性响应 Hessian 没有等于同一个 SCF Born–Oppenheimer 能量面的数值二阶导数？**

本计划的目标是把以下三件事逐级证明：

1. **真实势能面沿参考 `A_g` 模方向是稳定的。**
2. **误差来自 DFPT electronic-response 的对称二阶力常数，而不是最终对角化、ASR 或矩阵反对称部分。**
3. **进一步确定误差来自哪一段响应链：k/Fermi-surface、Sternheimer、Hartree/Hxc、2D Coulomb cutoff、occupation response，还是 PP-specific response。**

---

# 1. 所有后续实验必须固定的参考对象

后面不要再比较“每次计算得到的最低频模式”。不同 k 网格、smearing、PP、2D cutoff 等条件改变后，本征矢可能发生旋转，因此最低模编号不是稳定的比较对象。

应始终固定同一个参考位移方向 `e0`：

- 当前异常 `A_g` 模的参考本征矢；
- 或者固定当前已经确认与异常最相关的 rep7 / Te11/12/15/16 反相 z 位移模式；
- 所有计算中都保持同一个 Cartesian displacement pattern。

对任意动力学矩阵/力常数矩阵 `Φ`，统一计算参考方向上的 Rayleigh curvature：

```text
K(e0) = e0^T Φ e0
```

后面所有测试都至少同时报告：

```text
K_DFPT
K_E_FD
K_F_FD
ΔK = K_DFPT - K_FD
```

其中 `K_FD` 可以取 `K_E_FD` 与 `K_F_FD` 的平均值；在确认两者一致后，也可固定使用力曲率。

当前基线：

```text
K_E_FD   ≈ +24.9147 eV/Å²
K_F_FD   ≈ +24.9051 eV/Å²
K_DFPT   ≈ -104.8938 eV/Å²
ΔK       ≈ -129.8 eV/Å²
```

`ΔK` 是后面最重要的诊断量。

---

# 2. 总体证据树

推荐按照下面的顺序做，不要同时无序展开：

```text
A. FD 多振幅验证
        ↓
B. npool 不变性
        ↓
C. k 点 DFPT+FD 成对收敛
        ↓
D. smearing × k 点联合测试
        ↓
E. 2D cutoff ON/OFF：比较 ΔK 而不是单独比较 K
        ↓
F. 直接比较 n^(1)_DFPT 与 n^(1)_FD
        ↓
G. 比较 V_H^(1)_DFPT 与 V_H^(1)_FD
        ↓
H. 完整对称 waterfall block 重建
        ↓
I. vacuum thickness 测试
        ↓
J. independent DFPT code（优先 ABINIT）
```

每一步都要有明确的判据，见下文。

---

# 3. 实验 A：有限位移多振幅验证

## 3.1 目的

把“真实势能面正曲率”做成铁证，排除：

- 位移步长过大；
- 高阶非谐项污染；
- 非对称位移；
- 双井势；
- 单一 0.005 Å 点偶然误差。

## 3.2 建议位移幅度

对同一个参考方向 `e0`：

```text
Q = 0.0025 Å
Q = 0.0050 Å
Q = 0.0075 Å
Q = 0.0100 Å
```

每个幅度都做：

```text
-Q
 0
+Q
```

所有电子参数必须与基线完全一致。

## 3.3 能量曲率

定义：

```text
K_E(Q) = [E(+Q) + E(-Q) - 2E(0)] / Q²
```

如果势能是谐性的：

```text
E(Q) - E(0) ≈ 1/2 K Q²
```

应画：

```text
x = Q²
y = E(Q) - E(0)
```

做线性拟合。

## 3.4 力曲率

沿参考模式投影力：

```text
F_Q(Q) = Σ_i F_i(Q) · e0_i
```

定义：

```text
K_F(Q) = - [F_Q(+Q) - F_Q(-Q)] / (2Q)
```

应画：

```text
F_Q versus Q
```

若线性，则斜率为 `-K`。

## 3.5 判据

如果：

```text
K_E(Q) ≈ K_F(Q) ≈ +25 eV/Å²
```

并且 `Q → 0` 时稳定，则可强力结论：

> 当前 `A_g` 大虚频不是结构真实不稳定，也不是有限位移步长导致的假象。

---

# 4. 实验 B：npool 不变性测试

## 4.1 为什么必须做

当前已经发现：

- 某些 dump 只包含单 pool 的 k 点贡献；
- B21 dump 才是完整 64 k 求和。

因此必须把 **QE 并行归约/pool bookkeeping** 彻底排掉。

## 4.2 设置

同一个 SCF、同一个 `30×6×1` k 网格、同一个 `ph.in`：

```text
npool = 1
npool = 2
npool = 4
npool = 8
```

必要时可加：

```text
npool = 16
```

## 4.3 必须比较的量

至少比较：

```text
K_DFPT(e0)
完整 A_g 10×10 block
Phi_NL^sym
Phi_loc^sym
最终 dynmat
```

不要比较只来自单 pool 的中间 dump，除非已经在程序中显式做了全局归约。

## 4.4 判据

理论上：

```text
K_DFPT(npool=1)
= K_DFPT(npool=2)
= K_DFPT(npool=4)
= K_DFPT(npool=8)
```

如果不同：

> 优先诊断 parallel reduction / pool summation / dump bookkeeping，而不是讨论 Hartree、PP 或物理不稳定。

如果相同：

> 可以把 pool 并行本身排除。

---

# 5. 实验 C：k 点收敛——必须 DFPT 与 FD 成对做

## 5.1 核心思想

对于固定离散 k 网格 `Kmesh`，FD 和 DFPT 理论上都应该计算同一个离散电子自由能面的二阶导数：

```text
K_DFPT(Kmesh) ≈ K_FD(Kmesh)
```

即使 k 网格还没有收敛到连续 BZ 极限，两者也应该在同一个离散问题上相互一致。

所以真正要研究的不是单独的 `K_DFPT(Nk)`，而是：

```text
ΔK(Nk) = K_DFPT(Nk) - K_FD(Nk)
```

## 5.2 建议网格

晶胞约：

```text
a ≈ 3.737 Å
b ≈ 18.877 Å
```

`30×6` 在两个方向对应的倒空间采样间距几乎相同，因此保持约 5:1 的比例：

```text
20×4×1
30×6×1
40×8×1
50×10×1
```

必要时：

```text
60×12×1
```

## 5.3 每个 k 网格必须做什么

每个网格都同时做：

```text
1. SCF
2. DFPT Γ 点 reference-mode curvature
3. FD +Q / 0 / -Q
4. K_E_FD
5. K_F_FD
6. ΔK
```

建议固定 FD 位移为：

```text
Q = 0.005 Å
```

在实验 A 已证明线性区后即可。

## 5.4 必须画的图

三条曲线：

```text
K_DFPT(Nk)
K_FD(Nk)
ΔK(Nk)
```

## 5.5 结果解释

### 情况 C1：ΔK → 0

例如：

```text
20×4   FD +22   DFPT -150
30×6   FD +25   DFPT -105
40×8   FD +25   DFPT  -40
50×10  FD +25   DFPT  +10
60×12  FD +25   DFPT  +24
```

说明：

> 异常来自 metallic/Fermi-surface linear-response 的 k 点收敛问题。

更准确的表述不是“30×6 太稀”，而是：

> DFPT electronic response 对离散 Fermi-surface sampling 异常敏感，而 frozen-phonon curvature 已经较早收敛。

### 情况 C2：ΔK 保持约 -130 eV/Å²

例如：

```text
20×4   FD +22   DFPT -108
30×6   FD +25   DFPT -105
40×8   FD +25   DFPT -104
50×10  FD +25   DFPT -104
```

说明：

> 普通 k 点收敛不是根因，应转向 response formulation/implementation。

### 情况 C3：FD 与 DFPT 都剧烈随 k 点变化

说明：

> 体系本身 Fermi surface 收敛困难，需要进入 k 点 × smearing 联合测试。

---

# 6. 实验 D：k 点 × smearing 联合测试

## 6.1 目的

判断异常是否来自费米面附近的 occupation response / small-denominator electronic response。

## 6.2 建议最小矩阵

先不要把计算量做得太大。

选：

```text
k = 30×6×1
k = 40×8×1
```

smearing：

```text
0.025 eV
0.050 eV
0.075 eV
0.100 eV
```

所有组合都至少计算 `K_DFPT`；关键组合再补 `K_FD`。

## 6.3 关键诊断量

```text
ΔK(Nk, σ)
```

建议做二维 heatmap。

## 6.4 判据

如果：

```text
Nk ↑  → |ΔK| ↓
σ  ↑  → |ΔK| ↓
```

说明异常与 metallic Fermi-surface integration 强相关。

如果：

```text
ΔK ≈ -130 eV/Å²
```

在合理 `Nk`、`σ` 范围内基本不动，则可以明显降低 Fermi-surface sampling 作为主因的可能性。

---

# 7. 实验 E：2D Coulomb cutoff ON/OFF——比较 ΔK，不比较单独 K

## 7.1 目的

判断错误是否来自：

```text
assume_isolated='2D'
```

下的线性 Hartree/Coulomb response 路径。

## 7.2 两套独立物理模型

### E1：2D cutoff

```text
assume_isolated='2D'
```

分别计算：

```text
K_DFPT^2D
K_FD^2D
ΔK_2D = K_DFPT^2D - K_FD^2D
```

### E2：普通 3D periodic

去掉：

```text
assume_isolated='2D'
```

分别计算：

```text
K_DFPT^3D
K_FD^3D
ΔK_3D = K_DFPT^3D - K_FD^3D
```

## 7.3 重要注意

不要直接拿：

```text
K_2D versus K_3D
```

来判断 bug，因为两种边界条件本来就对应不同物理模型。

真正有意义的是比较：

```text
ΔK_2D versus ΔK_3D
```

## 7.4 强判据

如果：

```text
ΔK_2D ≈ -130 eV/Å²
ΔK_3D ≈ 0
```

则非常强地支持：

> QE 的 2D linear-response path 是异常来源。

如果两者都异常：

> 根因更可能位于更一般的 Sternheimer/Hxc/PP response，而不是 2D cutoff 专有代码。

---

# 8. 实验 F：直接比较 n^(1)_DFPT 与 n^(1)_FD

这是整个诊断中信息量最高的实验之一。

## 8.1 目的

判断错误究竟已经发生在：

```text
δV_SCF → δψ → δn
```

阶段，还是发生在得到正确 `δn` 之后的力常数组装阶段。

## 8.2 有限位移构造一阶密度

对 `+Q` 和 `-Q` 的完全自洽电子密度：

```text
n_FD^(1)(r)
= [n(+Q,r) - n(-Q,r)] / (2Q)
```

建议用实验 A 已确认在谐区内的：

```text
Q = 0.005 Å
```

并用 0.0025 Å 再做一次线性检查。

## 8.3 DFPT 一阶密度

从 `ph.x` 的响应自洽过程中 dump：

```text
n_DFPT^(1)(r)
```

必须确认：

- 是完整 k 求和后的全局量；
- 所有 pool 已正确归约；
- 与 FD 使用相同 normalization；
- 原子位移方向、单位、幅度定义完全一致。

## 8.4 比较方式

### 实空间

定义归一化差异：

```text
η_n = ||n_DFPT^(1) - n_FD^(1)|| / ||n_FD^(1)||
```

也要画：

```text
Δn_error(r) = n_DFPT^(1)(r) - n_FD^(1)(r)
```

### 倒空间

做 Fourier transform：

```text
n^(1)(G)
```

重点提取：

```text
G_parallel = 0
不同 G_z
```

因为当前异常模式主要是 Te 的 z 向反相/层间偶极位移。

## 8.5 判据

### F1：n_DFPT^(1) ≠ n_FD^(1)

说明错误已经发生在：

```text
Sternheimer / occupation response / self-consistent response
```

应重点继续查：

- k 点；
- smearing；
- Fermi-surface response；
- Sternheimer source term；
- PP projector response；
- Hxc self-consistency。

### F2：n_DFPT^(1) ≈ n_FD^(1)

但 `K_DFPT ≠ K_FD`：

说明一阶密度基本正确，错误更可能在：

```text
response → second-derivative / dynmat assembly
```

即：

- 二阶力常数组装；
- 某个 static/response correction；
- Coulomb/Hartree potential mapping；
- PP-specific second derivative term。

---

# 9. 实验 G：直接比较 V_H^(1)_DFPT 与 V_H^(1)_FD

## 9.1 为什么这一项特别重要

即使：

```text
||n_DFPT^(1)|| ≈ ||n_FD^(1)||
```

也不能说明 Hartree response 正确。

因为在倒空间：

```text
V_H^(1)(G) = v_c(G) n^(1)(G)
```

普通 3D 中：

```text
v_c(G) ∝ 1 / |G|²
```

因此少量低 `G` 分量可以被强烈放大。

## 9.2 有限位移构造 Hartree 一阶势

```text
V_H,FD^(1)(r)
= [V_H(+Q,r) - V_H(-Q,r)] / (2Q)
```

DFPT 直接 dump：

```text
V_H,DFPT^(1)(r)
```

## 9.3 倒空间分析

计算：

```text
V_H^(1)(G)
n^(1)(G)
```

定义：

```text
R_H(G) = V_H^(1)(G) / n^(1)(G)
```

理论上应复现所采用的 Coulomb kernel。

重点检查：

```text
G_parallel = 0
G_z → small
```

## 9.4 判据

### G1：n^(1) 一致，但 V_H^(1) 不一致

这是非常强的证据：

> 问题位于 Coulomb/Hartree kernel 或 2D response mapping，而不是 Sternheimer 产生的电子密度本身。

### G2：n^(1) 与 V_H^(1) 都一致，但 K_DFPT 仍错误

说明问题更下游：

> dynmat / second-derivative assembly。

---

# 10. 实验 H：完整对称 waterfall block 重建

## 10.1 目标

不能再只看某个 scalar headline 或某个 irrep 的单项幅度。

要尽量为每一类 contribution 重建完整的 `A_g 10×10` 矩阵：

```text
Phi_D0
Phi_loc
Phi_NL
Phi_NLCC
Phi_Hxc
Phi_occ
...（QE 中实际可拆出的全部项）
```

## 10.2 对称化

对每一项：

```text
Phi_i^S = 1/2 (Phi_i + Phi_i^T)
```

不要用反对称部分去解释最终实模式曲率，因为对于实向量 `c`：

```text
c^T (Phi - Phi^T) c = 0
```

当前 `Phi_NL` 的非厄米性已经证明不会进入实模式投影曲率。

## 10.3 固定参考模式投影

对同一个参考向量 `c0`：

```text
K_i = c0^T Phi_i^S c0
```

要求记账闭合：

```text
Σ_i K_i ≈ K_DFPT
```

如果不能闭合，说明 dump/分类/单位/pool 求和还存在问题，不能做物理归因。

## 10.4 定量描述“精细抵消”

定义 cancellation amplification factor：

```text
A_cancel = Σ_i |K_i| / |Σ_i K_i|
```

也可以记录：

```text
A_max = max_i |K_i| / |K_total|
```

如果 `A_cancel >> 1`，例如 `10²–10⁴`，就可以定量说明：

> 最终力常数是多个巨大 static/response contribution 高度抵消后的残差，因此很小的 response systematic error 就能翻转最终符号。

---

# 11. 实验 I：vacuum thickness 测试

## 11.1 建议真空/晶胞 c

```text
c = 25 Å
c = 34.2 Å  （当前）
c = 45 Å
c = 60 Å
```

## 11.2 两条线都做

### 2D cutoff

```text
assume_isolated='2D'
```

计算：

```text
K_DFPT^2D(c)
K_FD^2D(c)
ΔK_2D(c)
```

### 普通 3D periodic

计算：

```text
K_DFPT^3D(c)
K_FD^3D(c)
ΔK_3D(c)
```

## 11.3 判据

理想情况下：

```text
2D cutoff：物理结果对 c 应较快不敏感
3D periodic：会随 slab image interaction 逐渐收敛
```

更关键的是：

```text
ΔK_2D(c)
ΔK_3D(c)
```

如果 `ΔK_2D` 持续异常而 `ΔK_3D → 0`，会进一步支持 2D response path 问题。

---

# 12. 实验 J：独立 DFPT 实现交叉验证

## 12.1 推荐 ABINIT

目标不是简单“换软件”，而是尽量保持同一个 underlying pseudopotential dataset。

优先选择：

- PseudoDojo 同源 ONCV；
- QE 使用 UPF；
- ABINIT 使用同源 psp8。

## 12.2 第一阶段不要加入 2D cutoff

先使用：

```text
大真空 + 普通 3D periodic
```

比较：

```text
K_QE_DFPT
K_ABINIT_DFPT
K_FD
```

## 12.3 强判据

如果：

```text
K_ABINIT_DFPT ≈ K_FD > 0
K_QE_DFPT < 0
```

则是非常强的 QE-specific evidence。

如果 QE 与 ABINIT 都给负，而 FD 给正：

> 应重新检查共同的 PP/occupation/finite-T free-energy 定义，或有限位移与 DFPT 是否真的计算同一个 thermodynamic functional。

---

# 13. 每个实验必须统一记录的 metadata

建议每个测试生成一个 JSON/YAML，至少包括：

```yaml
qe_version:
pseudo_family:
pseudo_files:
ecutwfc:
ecutrho:
fft_grid:
fft_dense_grid:
kmesh:
kshift:
smearing:
degauss_eV:
nbnd:
assume_isolated:
cell_a:
cell_b:
cell_c:
npool:
ndiag:
tr2_ph:
alpha_mix:
nmix_ph:
reference_mode_id:
reference_mode_file:
fd_amplitude_A:
K_DFPT_eV_A2:
K_E_FD_eV_A2:
K_F_FD_eV_A2:
deltaK_eV_A2:
notes:
```

这样后面才能做批量图，而不是靠人工翻输出。

---

# 14. 推荐目录结构

建议新增：

```text
validation/
  01_fd_amplitude/
  02_npool/
  03_kmesh/
  04_kmesh_smearing/
  05_2d_on_off/
  06_drho_dfpt_vs_fd/
  07_vhartree_dfpt_vs_fd/
  08_waterfall_symmetric_blocks/
  09_vacuum/
  10_abinit_crosscheck/
```

每个目录包含：

```text
README.md
inputs/
outputs/
analysis/
result.json
```

---

# 15. 建议优先开发的分析脚本

## 15.1 `analyze_reference_curvature.py`

输入：

```text
reference_mode
DFPT dynmat / partial block
FD energies
FD forces
```

输出：

```text
K_DFPT
K_E_FD
K_F_FD
ΔK
```

所有后续实验统一调用。

## 15.2 `compare_kmesh_curvature.py`

自动读取多个 k 网格结果，生成：

```text
K_DFPT versus Nk
K_FD versus Nk
ΔK versus Nk
```

## 15.3 `compare_drho_dfpt_fd.py`

输出：

```text
||drho_DFPT||
||drho_FD||
relative error
real-space error map
G-space spectrum
G_parallel=0, G_z line
```

## 15.4 `compare_vhartree_dfpt_fd.py`

输出：

```text
V_H^(1)(G)
R_H(G)=V_H^(1)(G)/n^(1)(G)
G_parallel=0 comparison
```

## 15.5 `rebuild_waterfall_sym_blocks.py`

功能：

```text
读取各 waterfall contribution 的完整 A_g block
↓
做 pool/global k sum
↓
统一单位
↓
对称化
↓
沿 reference mode 投影
↓
检查 Σ_i K_i = K_DFPT
↓
计算 A_cancel
```

---

# 16. 当前已经基本排除的方向

根据现有结果，以下方向优先级已经明显降低：

## 16.1 真实结构不稳定

因为 FD 能量和力曲率都为正。

## 16.2 ASR / 最终对角化导致虚频

因为在 reference-mode / rep7 层面已经能观察到 DFPT 与 FD 符号冲突。

## 16.3 `Phi_NL` 反对称部分

对于实向量 `c`：

```text
c^T (Phi - Phi^T) c = 0
```

当前重建也数值验证到约 `1e-16`。

## 16.4 线性响应没有自洽

当前 response 已经达到非常严格的残差，不能用普通 SCF 未收敛解释。

## 16.5 Fermi-energy-shift divergence

当前 `DOS(E_F)` 与 `def` 并没有表现出已知 near-gap divergence 的特征。

## 16.6 单纯看 `drhodvnl` 很大就认为它有错

`Phi_NL` 中 Te 模式的大幅度本身可以是物理的；真正要检查的是：

```text
DFPT derivative 是否与 FD derivative 一致
```

而不是哪一项绝对值最大。

---

# 17. 当前最可能的根因层级

目前最合理的“本质”表述是：

> **Nb₂Pd₃Te₅ 的异常 Γ 点模式具有很强的 Te 主导电子屏蔽，最终力常数是多个巨大 static/response contribution 精细抵消后的较小残差。QE DFPT 的对称 electronic-response 二阶导数中存在一个相对于内部大项很小、但相对于最终残差很大的系统误差，从而把真实正曲率翻转为负曲率。**

目前尚未最终锁定的是这一个小 systematic error 的具体来源。

优先候选：

```text
1. metallic k/Fermi-surface response
2. Sternheimer/Hxc self-consistency 的某个对称分量
3. 2D Coulomb/Hartree response
4. PP-specific response implementation
5. second-derivative / dynmat assembly
```

---

# 18. 最关键的“分叉实验”

如果资源有限，只做三个最有信息量的实验：

## 18.1 k 点：DFPT + FD 成对

```text
30×6
40×8
50×10
```

看：

```text
ΔK(Nk)
```

## 18.2 2D cutoff ON/OFF：仍然成对做 DFPT + FD

看：

```text
ΔK_2D
ΔK_3D
```

## 18.3 n^(1)_DFPT vs n^(1)_FD

这是最关键的定位实验。

它能把问题直接分成：

```text
A. n^(1) 已经错
   → Sternheimer / metallic response / Hxc self-consistency

B. n^(1) 正确，但 V_H^(1) 错
   → Coulomb/Hartree/2D response

C. n^(1)、V_H^(1) 都正确，但 K 错
   → second-derivative / dynmat assembly
```

---

# 19. 最终希望形成的证据闭环

理想情况下，最终论文/issue 中的证据链应能写成：

```text
1. Multi-amplitude frozen phonon:
   K_E ≈ K_F > 0

2. Parallel invariance:
   npool does not change K_DFPT

3. k/smearing convergence:
   ΔK does not vanish under ordinary metallic convergence

4. 2D ON/OFF:
   identify whether the discrepancy is specific to the 2D response path

5. First-order response comparison:
   compare n^(1)_DFPT and n^(1)_FD

6. Hartree response comparison:
   compare V_H^(1)_DFPT and V_H^(1)_FD,
   especially G_parallel=0 and small G_z

7. Symmetric waterfall reconstruction:
   Σ_i K_i = K_DFPT exactly,
   quantify cancellation amplification

8. Independent DFPT implementation:
   QE versus ABINIT versus frozen phonon
```

最终目标不是只说：

> “QE 算出了假虚频。”

而是能够说清楚：

> **从哪一个响应量开始，DFPT 解析导数偏离了同一 Born–Oppenheimer 自由能面的数值导数；这个偏差如何经过强电子屏蔽和大项抵消被放大，最终导致力常数符号翻转。**

---

# 20. 建议当前立即执行的顺序

```text
Step 1  多振幅 FD：0.0025/0.005/0.0075/0.010 Å
Step 2  npool=1/2/4/8
Step 3  kmesh=20×4 / 30×6 / 40×8 / 50×10，DFPT+FD 成对
Step 4  30×6、40×8 上做 smearing 0.025–0.10 eV
Step 5  2D cutoff ON/OFF，比较 ΔK
Step 6  dump n^(1)_DFPT，并与 central-FD n^(1) 比较
Step 7  dump V_H^(1)_DFPT，并与 FD 比较 G_parallel=0 分量
Step 8  重建所有对称 waterfall block 并闭合记账
Step 9  vacuum thickness
Step 10 ABINIT cross-check
```

在 Step 6–7 之前，不建议继续仅凭某个 waterfall 子项“幅度最大”来指认根因。

真正有诊断意义的是：

```text
DFPT 的一阶/二阶解析响应
是否等于
同一 SCF 能量泛函的有限位移数值导数。
```

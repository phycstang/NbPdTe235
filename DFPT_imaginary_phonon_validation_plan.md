# Nb₂Pd₃Te₅ Γ 点 DFPT 假虚频：核心诊断分叉

更新日期：2026-09-17

## 目标

当前基线结果：

- `K_E(FD) ≈ +24.9147 eV/Å²`
- `K_F(FD) ≈ +24.9051 eV/Å²`
- `K_DFPT ≈ -104.8938 eV/Å²`
- `ΔK = K_DFPT - K_FD ≈ -129.8 eV/Å²`

说明真实 Born–Oppenheimer 势能面沿参考 `A_g` 模方向是正曲率，而 QE DFPT 给出了负曲率。

后续所有测试固定同一个参考位移方向 `e0`，不要比较“每次重新对角化后的最低模”。核心诊断量始终是：

```text
ΔK = K_DFPT(e0) - K_FD(e0)
```

---

# 核心诊断树

```text
                DFPT 与 FD 曲率符号相反
                         │
                         ▼
          ① 直接比较 n^(1)_DFPT 与 n^(1)_FD
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼                             ▼
 n^(1)_DFPT ≠ n^(1)_FD         n^(1)_DFPT ≈ n^(1)_FD
          │                             │
          ▼                             ▼
错误已发生在响应自洽链        ② 比较 V_H^(1)_DFPT 与 V_H^(1)_FD
          │                             │
          │                 ┌───────────┴───────────┐
          │                 │                       │
          ▼                 ▼                       ▼
查 Sternheimer /      V_H^(1) 不一致          V_H^(1) 也一致
k 点 / occupation /         │                       │
PP response                 ▼                       ▼
                    Hartree / Coulomb      错误在二阶力常数组装
                    kernel / 2D cutoff     dynmat / response terms
```

---

# 1. 第一关键实验：比较一阶密度响应

有限位移构造：

```text
n_FD^(1)(r) = [n(+Q,r) - n(-Q,r)] / (2Q)
```

DFPT 直接得到：

```text
n_DFPT^(1)(r)
```

必须比较：

```text
n_DFPT^(1)(r)  vs  n_FD^(1)(r)
```

并定义：

```text
η_n = ||n_DFPT^(1) - n_FD^(1)|| / ||n_FD^(1)||
```

不要只比较总范数，还要 Fourier transform 后比较：

```text
n^(1)(G)
```

尤其重点检查：

```text
G_parallel = 0
小 G_z
```

因为当前异常模式主要是 Te11/12/15/16 的反相 `z` 位移，具有明显层间偶极特征。

## 判据

### A. 如果

```text
n_DFPT^(1) ≠ n_FD^(1)
```

则错误已经发生在：

```text
δV_SCF → δψ → δn
```

此时重点检查：

```text
Sternheimer
k/Fermi-surface sampling
occupation response
PP/projector response
```

### B. 如果

```text
n_DFPT^(1) ≈ n_FD^(1)
```

则 Sternheimer 得到的一阶密度基本正确，继续进入下一分叉。

---

# 2. 第二关键实验：比较一阶 Hartree 势

有限位移构造：

```text
V_H,FD^(1)(r) = [V_H(+Q,r) - V_H(-Q,r)] / (2Q)
```

DFPT 对应：

```text
V_H,DFPT^(1)(r)
```

Fourier 空间比较：

```text
V_H^(1)(G)
```

并重点检查：

```text
G_parallel = 0
小 G_z
```

理论关系为：

```text
V_H^(1)(G) = v_c(G) n^(1)(G)
```

对于 `assume_isolated='2D'`，这里使用的是 2D Coulomb kernel。

## 判据

### A. 如果

```text
n_DFPT^(1) ≈ n_FD^(1)
```

但

```text
V_H,DFPT^(1) ≠ V_H,FD^(1)
```

尤其差异集中在：

```text
G_parallel = 0, 小 G_z
```

则强烈指向：

```text
Hartree response
2D Coulomb kernel
Coulomb cutoff response path
```

这是目前最有力的 2D-response 判据。

### B. 如果

```text
n^(1) 一致
V_H^(1) 也一致
```

但仍有：

```text
K_DFPT ≠ K_FD
```

则错误不在响应自洽本身，而在：

```text
一阶响应 → 二阶力常数
```

这时重点检查：

```text
dynmat assembly
drhodvloc
drhodvnl
NLCC
其他显式二阶项
```

并且只比较各项的**对称部分**：

```text
Phi_i^S = (Phi_i + Phi_i^T) / 2
```

因为已经证明反对称部分对实模式曲率不贡献。

---

# 3. 必做辅助判别：k 点是否是触发源

k 点测试只需要回答一个问题：

```text
ΔK(Nk) 是否随 k 点加密趋近 0？
```

建议：

```text
30×6×1
40×8×1
50×10×1
```

每个网格必须同时算：

```text
K_DFPT
K_FD
ΔK
```

## 判据

如果：

```text
ΔK → 0
```

则异常与 metallic/Fermi-surface linear-response 的 k 点收敛强相关。

如果：

```text
ΔK ≈ -130 eV/Å²
```

基本不变，则普通 k 点收敛不是根因。

注意：即使加密 k 点使异常消失，也应描述为：

> DFPT electronic response 对 Fermi-surface sampling 异常敏感。

而不是简单写成“30×6×1 太稀”。

---

# 4. 必做辅助判别：2D cutoff ON/OFF

分别计算：

```text
ΔK_2D = K_DFPT^2D - K_FD^2D
```

和

```text
ΔK_3D = K_DFPT^3D - K_FD^3D
```

不要直接比较 `K_2D` 与 `K_3D`，因为两种边界条件本来就是不同物理模型。

## 强判据

如果：

```text
ΔK_2D ≈ -130 eV/Å²
ΔK_3D ≈ 0
```

则非常强地支持：

```text
QE 2D Hartree/Coulomb linear-response path
```

是异常来源。

如果两者都异常，则根因更可能位于更一般的 Sternheimer / PP / second-derivative assembly 中。

---

# 5. 最终结论分叉

## 分叉 1

```text
n_DFPT^(1) ≠ n_FD^(1)
```

结论：

```text
错误发生在一阶电子响应自洽阶段
```

优先查：

```text
Sternheimer
k/Fermi-surface
occupation response
PP/projector response
```

---

## 分叉 2

```text
n_DFPT^(1) ≈ n_FD^(1)
V_H,DFPT^(1) ≠ V_H,FD^(1)
```

结论：

```text
错误集中在 Hartree/Coulomb response
```

如果同时满足：

```text
ΔK_2D ≠ 0
ΔK_3D ≈ 0
```

则可以进一步定位为：

```text
2D Coulomb cutoff linear-response path
```

---

## 分叉 3

```text
n^(1) 一致
V_H^(1) 一致
K_DFPT ≠ K_FD
```

结论：

```text
错误发生在二阶力常数的组装阶段
```

重点检查：

```text
symmetric drhodvloc
a symmetric drhodvnl block
NLCC symmetric contribution
explicit second derivatives
dynmat construction
```

其中应写作：

```text
symmetric drhodvnl block
```

而不是把已经证明无贡献的反对称部分重新作为嫌疑对象。

---

# 6. 当前最重要的执行顺序

只保留四步：

```text
1. n_DFPT^(1) vs n_FD^(1)
2. V_H,DFPT^(1) vs V_H,FD^(1)
3. ΔK(k-point) 收敛
4. ΔK_2D vs ΔK_3D
```

这四步足以把目前主要候选机制分开。

最关键的一步是第 1 步：

```text
直接比较 DFPT 一阶响应与有限位移数值一阶导数
```

它决定下一步究竟应该继续追 Sternheimer，还是转向 Hartree/2D cutoff，或者最终转向二阶 dynmat assembly。

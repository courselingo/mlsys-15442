# mlsys-15442/figures/deep-learning-abstraction-13.svg

模型 qwen3.8-max
复核对象 SHA256(前16)：`8CE82362FFCD7823`
SVG mtime：2026-09-29 09:40:02

## 版面
共两行。第一行四列方框，自左至右为：x（输入）、matmul（矩阵乘）、softmax（归一化成概率）、y（预测）；第二行仅一列方框 W（权重矩阵），位于 matmul 框正下方。箭头共四个：第一行三个水平向右箭头，依次为 x→matmul、matmul→softmax、softmax→y；另有一个垂直向上箭头，由 W 框顶边指向 matmul 框底边。

## 全部文字
案例的前向部分：从输入与权重到预测
x
输入
matmul
矩阵乘
softmax
归一化成概率
y
预测
W
权重矩阵

## 缺陷
未发现

## 判定
判定：可用 流程顺序、箭头方向与公式含义（y=softmax(x·W)）一致，文字完整居中、无碰撞或溢出。

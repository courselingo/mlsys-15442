/* MathJax —— 给算法 / 大模型这类含公式的课程用。
 *
 * 参考同类项目（yeasy/llm_internals）用 $$ 写公式，我们目前没有公式渲染，
 * 要覆盖那类课程就必须补上。这里用 Material 推荐的 arithmatex(generic) + MathJax 组合。
 *
 * 注意：MathJax 从 CDN 加载，属**运行时外部依赖**。离线环境或 CDN 不可达时
 * 公式不会渲染（正文其余部分不受影响）。若要完全离线，需把 MathJax 打包进仓库。
 */
window.MathJax = {
  tex: {
    inlineMath: [
      ['\\(', '\\)'],
      ['$', '$'],
    ],
    displayMath: [
      ['$$', '$$'],
      ['\\[', '\\]'],
    ],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    ignoreHtmlClass: '.*|',
    processHtmlClass: 'arithmatex',
  },
}

document$.subscribe(() => {
  if (window.MathJax && window.MathJax.typesetPromise) {
    window.MathJax.typesetPromise()
  }
})

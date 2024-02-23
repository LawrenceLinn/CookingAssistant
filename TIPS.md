运行 ESLint：检查 JavaScript 和 TypeScript 代码质量和风格问题。
```bash
npx eslint . --ext .js,.jsx,.ts,.tsx
```
运行 Prettier：自动格式化代码以保持一致的风格。
```bash
npx prettier --write .
```
运行 TypeScript 编译器：检查类型错误。
```bash
npx tsc --noEmit
```
--noEmit 选项告诉 TypeScript 只进行类型检查，不输出文件。

```bash
black .
```

const rows = [0,1,2,3,4,5,6,7,8,9]
const columns = [0,1,2,3,4,5,6,7,8,9]
const matrix = rows.map((row, count) => columns.map((column) => Math.floor(Math.random() * 101)))

matrix.forEach(row => console.log(row.join(' ')))

const maxInRowsWithIndices = matrix.map((row, rowIndex) => {
  const maxInRow = Math.max(...row)
  const columnIndex = row.indexOf(maxInRow)
  return { maxInRow, rowIndex, columnIndex }
})

console.log("Максимальные элементы в строках и их позиции:")
maxInRowsWithIndices.forEach(({ maxInRow, rowIndex, columnIndex }) => {
  console.log(`Строка ${rowIndex}: Максимум = ${maxInRow}, Колонка = ${columnIndex}`)
})

const { maxInRow: maxElement, rowIndex: maxRowIndex, columnIndex: maxColIndex } =
  maxInRowsWithIndices.reduce((max, current) => {
    return current.maxInRow > max.maxInRow ? current : max
  })

console.log(`Максимальный элемент в матрице: ${maxElement}`)
console.log(`Расположение максимального элемента: Строка ${maxRowIndex}, Колонка ${maxColIndex}`)

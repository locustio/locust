import {
  Paper,
  Table as MuiTable,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

import { ITableStructure } from 'types/table.types';
import { roundToDecimalPlaces } from 'utils/number';

interface ITable<Row> {
  rows: Row[];
  structure: ITableStructure[];
  children?: React.ReactElement;
}

export interface ITableRowProps {
  className?: string;
  text?: string;
  structureKey?: string;
}

export default function Table<Row extends Record<string, any> = Record<string, string | number>>({
  rows,
  structure,
}: ITable<Row>) {
  return (
    <TableContainer component={Paper}>
      <MuiTable>
        <TableHead>
          <TableRow>
            {structure.map(({ title, key }) => (
              <TableCell key={`table-head-${key}`}>{title}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row, index) => (
            <TableRow key={`${row.name}-${index}`}>
              {structure.map(({ key, round }, index) => (
                <TableCell key={`table-row=${index}`}>
                  {round ? roundToDecimalPlaces(row[key], round) : row[key]}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </MuiTable>
    </TableContainer>
  );
}

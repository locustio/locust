import {
  Paper,
  Table as MuiTable,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import Markdown from 'react-markdown';

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

export interface ITableRowContent {
  content: string | number;
  round?: number;
  markdown?: boolean;
}

function TableRowContent({ content, round, markdown }: ITableRowContent) {
  if (round) {
    return roundToDecimalPlaces(content as number, round);
  }

  if (markdown) {
    return <Markdown skipHtml={false}>{content as string}</Markdown>;
  }

  return content;
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
              {structure.map(({ key, round, markdown }, index) => (
                <TableCell key={`table-row=${index}`}>
                  <TableRowContent content={row[key]} markdown={markdown} round={round} />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </MuiTable>
    </TableContainer>
  );
}

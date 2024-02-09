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

import useSortByField, { ISortByFieldOptions } from 'hooks/useSortByField';
import { ITableStructure } from 'types/table.types';
import { roundToDecimalPlaces } from 'utils/number';

interface ITable<Row> extends ISortByFieldOptions<Row> {
  rows: Row[];
  structure: ITableStructure[];
  children?: React.ReactElement;
  onTableHeadClick?: (event: React.MouseEvent<HTMLElement>) => void;
  currentSortField?: string;
}

export interface ITableRowProps {
  className?: string;
  text?: string;
  structureKey?: string;
}

export interface ITableRowContent {
  content: string | number;
  formatter?: (content: string | number) => string;
  round?: number;
  markdown?: boolean;
}

function TableRowContent({ content, formatter, round, markdown }: ITableRowContent) {
  if (formatter) {
    return formatter(content);
  }

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
  hasTotalRow,
  defaultSortKey,
}: ITable<Row>) {
  const { onTableHeadClick, sortedRows, currentSortField } = useSortByField<Row>(rows, {
    hasTotalRow,
    defaultSortKey,
  });

  return (
    <TableContainer component={Paper}>
      <MuiTable>
        <TableHead>
          <TableRow>
            {structure.map(({ title, key }) => (
              <TableCell
                data-sortkey={key}
                key={`table-head-${key}`}
                onClick={onTableHeadClick}
                sx={{
                  cursor: 'pointer',
                  color: currentSortField === key ? 'primary.main' : 'text.primary',
                }}
              >
                {title}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {sortedRows.map((row, index) => (
            <TableRow key={`${row.name}-${index}`}>
              {structure.map(({ key, ...tableRowProps }, index) => (
                <TableCell key={`table-row=${index}`}>
                  <TableRowContent content={row[key]} {...tableRowProps} />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </MuiTable>
    </TableContainer>
  );
}

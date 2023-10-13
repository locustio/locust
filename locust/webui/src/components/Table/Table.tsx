import {
  Paper,
  Table as MuiTable,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  SelectChangeEvent,
} from '@mui/material';
import Markdown from 'react-markdown';

import Select from 'components/Form/Select';
import { useAction, useSelector } from 'redux/hooks';
import { uiActions } from 'redux/slice/ui.slice';
import { ITableStructure } from 'types/table.types';
import { ITableState } from 'types/ui.types';
import { roundToDecimalPlaces } from 'utils/number';

type BaseRow = Record<string, string | number>;

interface IBaseTable<Row> {
  groupBy?: string;
  rows: Row[];
  structure: ITableStructure[];
  onTableHeadClick?: (event: React.MouseEvent<HTMLElement>) => void;
  currentSortField?: string;
}

interface IGroupedTableWithSelect<Row> extends IBaseTable<Row> {
  label: string;
  groupOptions: string[];
}

interface IGroupedTable<Row> extends IBaseTable<Row> {
  children?: React.ReactElement;
}

interface ITable<Row> extends IBaseTable<Row> {
  label?: string;
  groupOptions?: string[] | false;
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

function BaseTable<Row extends Record<string, any> = BaseRow>({
  rows,
  structure,
  onTableHeadClick,
  currentSortField,
}: IBaseTable<Row>) {
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
                  cursor: onTableHeadClick ? 'pointer' : 'default',
                  color: currentSortField === key ? 'primary.main' : 'text.primary',
                }}
              >
                {title}
              </TableCell>
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

function GroupedTableWithSelect<Row extends Record<string, any> = BaseRow>({
  label,
  groupOptions,
  ...baseTableProps
}: IGroupedTableWithSelect<Row>) {
  const updateTable = useAction(uiActions.updateTable);
  const { groupBy } = useSelector(
    ({ ui: { tables } }) => (label && tables[label]) || ({} as ITableState),
  );

  const onChange = (event: SelectChangeEvent<unknown>) => {
    const selectedGroupOption = event.target.value as string;
    const selectedGroupByValue = selectedGroupOption !== 'None' ? selectedGroupOption : undefined;

    updateTable({ label, state: { groupBy: selectedGroupByValue } });
  };

  return (
    <GroupedTable groupBy={groupBy} {...baseTableProps}>
      <Select
        defaultValue={groupBy}
        label='Group By'
        name='groupBy'
        onChange={onChange}
        options={['None', ...groupOptions]}
        sx={{ my: 2 }}
      />
    </GroupedTable>
  );
}

function GroupedTable<Row extends Record<string, any> = BaseRow>({
  rows,
  groupBy,
  children,
  ...baseTableProps
}: IGroupedTable<Row>) {
  const groupedRows =
    groupBy &&
    rows.reduce(
      (groups: { [key: string]: Row[] }, row) => ({
        ...groups,
        [row[groupBy]]: groups[row[groupBy] as string]
          ? [...groups[row[groupBy] as string], row]
          : [row],
      }),
      {},
    );

  return (
    <Paper sx={{ width: '100%', p: 2 }}>
      {children && children}

      {groupBy ? (
        Object.entries(groupedRows as { [key: string]: Row[] }).map(([group, groupedRows]) => (
          <Box sx={{ my: 2 }}>
            {group && (
              <Typography component='div' id='tableTitle' sx={{ flex: '1 1 100%' }} variant='h6'>
                {group}
              </Typography>
            )}
            <BaseTable {...baseTableProps} rows={groupedRows} />
          </Box>
        ))
      ) : (
        <BaseTable {...baseTableProps} rows={rows} />
      )}
    </Paper>
  );
}

export default function Table<Row extends Record<string, any> = BaseRow>({
  rows,
  groupOptions,
  label,
  groupBy,
  ...baseTableProps
}: ITable<Row>) {
  if (groupBy) {
    return <GroupedTable<Row> groupBy={groupBy} rows={rows} {...baseTableProps} />;
  }

  if (label && groupOptions) {
    return (
      <GroupedTableWithSelect<Row>
        groupOptions={groupOptions}
        label={label}
        rows={rows}
        {...baseTableProps}
      />
    );
  }

  return <BaseTable<Row> {...baseTableProps} rows={rows} />;
}

import { useState } from 'react';
import ViewColumnIcon from '@mui/icons-material/ViewColumn';
import { Button, FormControlLabel, FormGroup, Popover, Stack, Switch } from '@mui/material';

import { ITableStructure } from 'types/table.types';

interface IViewColumnSelector {
  structure: ITableStructure[];
  selectedColumns: string[];
  addColumn: (column: string) => void;
  removeColumn: (column: string) => void;
}

function ViewColumnSelector({
  structure,
  selectedColumns,
  addColumn,
  removeColumn,
}: IViewColumnSelector) {
  const [anchorEl, setAnchorEl] = useState(null as HTMLButtonElement | null);

  return (
    <Stack direction='row' justifyContent='end' my={2} spacing={1}>
      <Button onClick={event => setAnchorEl(event.currentTarget)} variant='outlined'>
        <ViewColumnIcon />
      </Button>
      <Popover
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        onClose={() => setAnchorEl(null)}
        open={Boolean(anchorEl)}
      >
        <FormGroup sx={{ p: 2 }}>
          {structure.map(({ key, title }) => (
            <FormControlLabel
              control={
                <Switch
                  checked={selectedColumns.includes(key)}
                  onChange={() => {
                    if (selectedColumns.includes(key)) {
                      removeColumn(key);
                    } else {
                      addColumn(key);
                    }
                  }}
                />
              }
              key={key}
              label={title}
            />
          ))}
        </FormGroup>
      </Popover>
    </Stack>
  );
}

export default ViewColumnSelector;

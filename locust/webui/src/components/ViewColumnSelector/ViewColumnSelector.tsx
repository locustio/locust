import { useState } from 'react';
import ViewColumnIcon from '@mui/icons-material/ViewColumn';
import { Box, Button, FormControlLabel, FormGroup, Popover, Switch } from '@mui/material';

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
    <Box sx={{ display: 'flex', justifyContent: 'flex-end', my: 2 }}>
      <Button onClick={event => setAnchorEl(event.currentTarget)} variant='outlined'>
        <ViewColumnIcon />
      </Button>
      <Popover
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        onClose={() => setAnchorEl(null)}
        open={Boolean(anchorEl)}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
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
    </Box>
  );
}

export default ViewColumnSelector;

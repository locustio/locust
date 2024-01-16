import { render, fireEvent, screen } from '@testing-library/react';
import { describe, expect, test, vi } from 'vitest';

import ViewColumnSelector from './ViewColumnSelector';

describe('ViewColumnSelector', () => {
  const mockStructure = [
    { key: 'column1', title: 'Column 1' },
    { key: 'column2', title: 'Column 2' },
  ];
  const mockSelectedColumns = ['column1'];
  const mockAddColumn = vi.fn();
  const mockRemoveColumn = vi.fn();

  test('should render switches for each structure item', () => {
    render(
      <ViewColumnSelector
        addColumn={mockAddColumn}
        removeColumn={mockRemoveColumn}
        selectedColumns={mockSelectedColumns}
        structure={mockStructure}
      />,
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    const switches = screen.getAllByRole('checkbox');
    expect(switches.length).toEqual(mockStructure.length);
  });

  test('should toggle switches correctly', () => {
    render(
      <ViewColumnSelector
        addColumn={mockAddColumn}
        removeColumn={mockRemoveColumn}
        selectedColumns={mockSelectedColumns}
        structure={mockStructure}
      />,
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    // Initial state check: 'column1' should be on and 'column2' should be off
    const switch1 = screen.getByLabelText('Column 1');
    const switch2 = screen.getByLabelText('Column 2');

    // Click on 'column2' switch to add the column
    fireEvent.click(switch2);
    expect(mockAddColumn).toHaveBeenCalledWith('column2');

    // Click on 'column1' switch to remove the column
    fireEvent.click(switch1);
    expect(mockRemoveColumn).toHaveBeenCalledWith('column1');
  });
});

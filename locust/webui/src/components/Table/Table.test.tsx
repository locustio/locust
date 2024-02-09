import { render } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import Table from 'components/Table/Table';
import { roundToDecimalPlaces } from 'utils/number';

const mockRows = [
  { method: 'GET', name: '/test1', numRequests: '2' },
  { method: 'POST', name: '/test2', numRequests: '10' },
  { method: 'PUT', name: '/test3', numRequests: '1' },
  { method: 'DELETE', name: '/test4', numRequests: '0' },
];

const mockStructure = [
  { title: 'Method', key: 'method' },
  { title: 'Name', key: 'name' },
  { title: '# Requests', key: 'numRequests' },
];

describe('Table', () => {
  test('renders table header and rows correctly', () => {
    const { getByText, getAllByRole } = render(<Table rows={mockRows} structure={mockStructure} />);

    mockStructure.forEach(({ title }) => {
      expect(getByText(title)).toBeTruthy();
    });

    mockRows.forEach(row => {
      Object.values(row).forEach(value => {
        expect(getByText(value.toString())).toBeTruthy();
      });
    });

    const rows = getAllByRole('row');
    expect(rows.length).toBe(mockRows.length + 1); // +1 for the header row
  });

  test('rounds numeric content to the specified decimal places', () => {
    const mockStructureWithRps = [{ title: 'Current RPS', key: 'currentRps', round: 2 }];
    const mockRowsWithRps = [
      { method: 'GET', name: '/test1', numRequests: '2', currentRps: 2.222 },
    ];

    const { getByText } = render(<Table rows={mockRowsWithRps} structure={mockStructureWithRps} />);

    expect(getByText(roundToDecimalPlaces(mockRowsWithRps[0].currentRps, 2))).toBeTruthy();
  });

  test('parses special HTML symbols into characters', () => {
    const mockStructureWithMarkdown = [{ title: 'Message', key: 'error', markdown: true }];
    const mockRowsWithRps = [
      {
        method: 'GET',
        name: '/test1',
        occurrences: 1,
        error: 'ConnectionRefusedError(111, &#x27;Connection refused&#x27;)',
      },
    ];

    const { getByText } = render(
      <Table rows={mockRowsWithRps} structure={mockStructureWithMarkdown} />,
    );

    expect(getByText("ConnectionRefusedError(111, 'Connection refused')")).toBeTruthy();
  });

  test('formats row content according to a provided formatter', () => {
    const rowContent = 'message';

    const rowContentFormatter = (content: string) => `Formatted! ${content}`;

    const mockStructureWithFormatter = [
      {
        title: 'Formatted Message',
        key: 'formattedMessage',
        formatter: rowContentFormatter,
      },
    ];

    const mockRowsWithRps = [
      {
        formattedMessage: rowContent,
      },
    ];

    const { getByText } = render(
      <Table rows={mockRowsWithRps} structure={mockStructureWithFormatter} />,
    );

    expect(getByText(rowContentFormatter(rowContent))).toBeTruthy();
  });
});

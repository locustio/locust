import { describe, test, expect } from 'vitest';

import SwarmRatios from 'components/SwarmRatios/SwarmRatios';
import { renderWithProvider } from 'test/testUtils';

describe('SwarmRatios', () => {
  test('should render nothing when no ratios are provided', () => {
    const { container } = renderWithProvider(<SwarmRatios />);

    expect(container.innerHTML).toEqual('');
  });

  test('should render perClass ratios when provided', () => {
    const { getByText } = renderWithProvider(<SwarmRatios />, {
      ui: {
        ratios: {
          perClass: {
            class1: { ratio: 0.2, tasks: { nested1: { ratio: 0.3 } } },
            class2: { ratio: 0.8 },
          },
        },
      },
    });

    expect(getByText('Ratio Per Class')).toBeTruthy();
    expect(getByText('20.0% class1')).toBeTruthy();
    expect(getByText('80.0% class2')).toBeTruthy();
    expect(getByText('30.0% nested1')).toBeTruthy();
  });

  test('should only allow a single decimal', () => {
    const { getByText } = renderWithProvider(<SwarmRatios />, {
      ui: {
        ratios: {
          perClass: {
            class1: { ratio: 0.223, tasks: { nested1: { ratio: 0.3462 } } },
            class2: { ratio: 0.888888888 },
          },
        },
      },
    });

    expect(getByText('Ratio Per Class')).toBeTruthy();
    expect(getByText('22.3% class1')).toBeTruthy();
    expect(getByText('88.9% class2')).toBeTruthy();
    expect(getByText('34.6% nested1')).toBeTruthy();
  });

  test('should render total ratios when provided', () => {
    const { getByText } = renderWithProvider(<SwarmRatios />, {
      ui: {
        ratios: {
          total: {
            total1: { ratio: 0.5, tasks: { nested2: { ratio: 0.6 } } },
          },
        },
      },
    });

    expect(getByText('Total Ratio')).toBeTruthy();
    expect(getByText('50.0% total1')).toBeTruthy();
    expect(getByText('60.0% nested2')).toBeTruthy();
  });

  test('should render both perClass and total ratios when provided', () => {
    const { getByText } = renderWithProvider(<SwarmRatios />, {
      ui: {
        ratios: {
          perClass: {
            class1: { ratio: 0.2, tasks: { nested1: { ratio: 0.3 } } },
          },
          total: {
            total1: { ratio: 0.5, tasks: { nested2: { ratio: 0.6 } } },
          },
        },
      },
    });

    expect(getByText('Ratio Per Class')).toBeTruthy();
    expect(getByText('Total Ratio')).toBeTruthy();
    expect(getByText('20.0% class1')).toBeTruthy();
    expect(getByText('50.0% total1')).toBeTruthy();
    expect(getByText('30.0% nested1')).toBeTruthy();
    expect(getByText('60.0% nested2')).toBeTruthy();
  });
});

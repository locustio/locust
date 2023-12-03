import { act } from '@testing-library/react';
import { test, describe, expect } from 'vitest';

import Tabs from 'components/Tabs/Tabs';
import { baseTabs, conditionalTabs } from 'components/Tabs/Tabs.constants';
import { renderWithProvider } from 'test/testUtils';
import { getUrlParams } from 'utils/url';

describe('Tabs', () => {
  test('renders the component with base tabs', () => {
    const { getByText } = renderWithProvider(<Tabs />);

    baseTabs.forEach(({ title }) => {
      expect(getByText(title)).toBeTruthy();
    });
  });

  test('renders the component with conditional tabs based on state', () => {
    const { getByText } = renderWithProvider(<Tabs />, {
      swarm: { isDistributed: true },
    });

    conditionalTabs.forEach(({ title }) => {
      expect(getByText(title)).toBeTruthy();
    });
  });

  test('does not render the conditional tabs when condition is falsy', () => {
    const { queryByText } = renderWithProvider(<Tabs />, {
      swarm: { isDistributed: false },
    });

    conditionalTabs.forEach(({ title }) => {
      expect(queryByText(title)).toBeNull();
    });
  });

  test('renders the component with extended tabs', () => {
    const { getByText } = renderWithProvider(<Tabs />, {
      swarm: {
        extendedTabs: [{ key: 'content-length', title: 'Content Length' }],
      },
    });

    expect(getByText('Content Length')).toBeTruthy();
  });

  test('appends the current tab to url query and url state and changes view on tab click', () => {
    const { getByText, store } = renderWithProvider(<Tabs />);

    const tabToSelect = baseTabs[2].title;
    const tabState = { tab: baseTabs[2].key };
    const tabElement = getByText(tabToSelect);

    act(() => {
      tabElement.click();
    });

    expect(getUrlParams()).toEqual(tabState);
    expect(store.getState().url.query).toEqual(tabState);
    expect(getByText('# Failures')).toBeTruthy();
  });
});

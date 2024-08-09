import { useEffect } from 'react';

import { useAction, useSelector } from 'redux/hooks';
import { notificationActions } from 'redux/slice/notification.slice';

export default function useNotifications(
  data: any[],
  { key, shouldNotify }: { key: string; shouldNotify?: (key: string) => boolean },
) {
  const setNotification = useAction(notificationActions.setNotification);
  const currentPage = useSelector(({ url: { query } }) => query && query.tab);
  const storageKey = `${key}Notification`;

  useEffect(() => {
    // handles data being reset
    // localStorage should always be <= to data.length
    if (data.length > 0 && data.length < localStorage[storageKey]) {
      localStorage[storageKey] = data.length;
    }

    if (
      data.length > (localStorage[storageKey] || 0) &&
      // no current page means no tabs have been clicked and notifications should be shown
      // don't show notifications for current page
      (!currentPage || currentPage !== key) &&
      // allows to customize if notification should be shown
      (!shouldNotify || (shouldNotify && shouldNotify(storageKey)))
    ) {
      setNotification({ [key]: true });
      localStorage[storageKey] = data.length;
    }
  }, [data]);
}

import { useEffect } from 'react';

import { useAction, useSelector } from 'redux/hooks';
import { notificationActions } from 'redux/slice/notification.slice';
import { objectLength } from 'utils/object';

export default function useNotifications(
  data: any[] | Record<string, any>,
  { key, shouldNotify }: { key: string; shouldNotify?: () => boolean },
) {
  const setNotification = useAction(notificationActions.setNotification);
  const currentPage = useSelector(({ url: { query } }) => query && query.tab);
  const storageKey = `${key}Notification`;

  useEffect(() => {
    if (objectLength(data) > 0 && objectLength(data) < localStorage[storageKey]) {
      // handles data being reset
      // localStorage should always be <= to objectLength(data)
      localStorage[storageKey] = objectLength(data);
    }

    if (
      objectLength(data) > (localStorage[storageKey] || 0) &&
      /// don't show notifications for current page
      (!currentPage || currentPage !== key) &&
      // allows to customize if notification should be shown
      (!shouldNotify || (shouldNotify && shouldNotify()))
    ) {
      setNotification({ [key]: true });
      localStorage[storageKey] = objectLength(data);
    }
  }, [data]);
}

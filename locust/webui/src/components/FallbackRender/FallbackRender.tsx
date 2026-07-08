import type { FallbackProps } from 'react-error-boundary';

export default function FallbackRender({ error }: FallbackProps) {
  return (
    <div role='alert'>
      <p>Something went wrong</p>
      {error instanceof Error && error.message && (
        <pre style={{ color: 'red' }}>{error.message}</pre>
      )}
      If the issue persists, please consider opening an{' '}
      <a href='https://github.com/locustio/locust/issues/new?assignees=&labels=bug&projects=&template=bug.yml'>
        issue
      </a>
    </div>
  );
}

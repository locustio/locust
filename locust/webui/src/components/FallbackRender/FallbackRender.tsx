export default function FallbackRender({ error }: { error: { message?: string } }) {
  return (
    <div role='alert'>
      <p>Something went wrong</p>
      {error.message && <pre style={{ color: 'red' }}>{error.message}</pre>}
      If the issue persists, please consider opening an{' '}
      <a href='https://github.com/locustio/locust/issues/new?assignees=&labels=bug&projects=&template=bug.yml'>
        issue
      </a>
    </div>
  );
}

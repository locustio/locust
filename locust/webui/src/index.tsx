import ReactDOM from 'react-dom/client';
import { ErrorBoundary } from 'react-error-boundary';
import { io, Socket } from "socket.io-client";

import App from 'App';
import FallbackRender from 'components/FallbackRender/FallbackRender';

interface ServerToClientEvents {
  request: (row: string) => void;
}

interface ClientToServerEvents {
  // hello: () => void;
}

const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io();

socket.on("request", (row) => {
  console.log(row);
});

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
  <ErrorBoundary fallbackRender={FallbackRender}>
    <App />
  </ErrorBoundary>,
);

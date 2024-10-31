import { Link } from '@mui/material';
import ReactMarkdown from 'react-markdown';

type CustomMarkdownLink = (props: {
  href?: string;
  children?: React.ReactNode;
}) => React.ReactElement;

export default function Markdown({ content }: { content: string }) {
  return (
    <ReactMarkdown components={{ a: Link as CustomMarkdownLink }} skipHtml={false}>
      {content}
    </ReactMarkdown>
  );
}

import { ProductImage } from './ProductImage';

// Only these text conventions are supported. HTML is rendered as plain text by React.
function InlineText({ text }) {
  const parts = text.split(/(\*\*[^*\n]+\*\*|\*[^*\n]+\*|\[[^\]\n]+\]\([^\s)]+\))/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (part.startsWith('*') && part.endsWith('*')) return <em key={index}>{part.slice(1, -1)}</em>;
    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (link && /^(https?:\/\/|mailto:|#\/)/i.test(link[2]))
      return (
        <a key={index} href={link[2]}>
          {link[1]}
        </a>
      );
    return part;
  });
}

export function FormattedText({ text }) {
  const lines = text.split('\n');
  const elements = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      const Tag = heading[1].length === 3 ? 'h3' : 'h2';
      elements.push(
        <Tag key={i}>
          <InlineText text={heading[2]} />
        </Tag>,
      );
      continue;
    }
    const list = line.match(/^(- |\d+\. )/);
    if (list) {
      const ordered = list[1] !== '- ';
      const pattern = ordered ? /^\d+\. / : /^- /;
      const items = [];
      const key = i;
      while (i < lines.length && pattern.test(lines[i])) {
        items.push(
          <li key={i}>
            <InlineText text={lines[i].replace(pattern, '')} />
          </li>,
        );
        i++;
      }
      i--;
      elements.push(ordered ? <ol key={key}>{items}</ol> : <ul key={key}>{items}</ul>);
      continue;
    }
    elements.push(
      <p key={i}>
        <InlineText text={line} />
      </p>,
    );
  }
  return <div className="about-prose">{elements}</div>;
}

export function AboutContent({ page }) {
  return (
    <article className="about-content">
      <h1>{page.title}</h1>
      {page.blocks.map((block, index) =>
        block.type === 'image' ? (
          <figure className="about-photo" key={index}>
            <ProductImage
              image={{ image_url: block.image_url, alt_text: block.alt || block.caption }}
              alt="Фотография мастерской"
            />
            {block.caption && <figcaption>{block.caption}</figcaption>}
          </figure>
        ) : (
          <FormattedText key={index} text={block.text} />
        ),
      )}
    </article>
  );
}

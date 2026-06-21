interface ConceptExplainerProps {
  text: string;
}

export function ConceptExplainer({ text }: ConceptExplainerProps) {
  // Parse markdown-style bold (**text**) into <strong> tags
  const parseMarkdown = (md: string) => {
    return md.split('\n').map((line, i) => {
      // Handle bold
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const rendered = parts.map((part, j) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={j}>{part.slice(2, -2)}</strong>;
        }
        return part;
      });

      return (
        <p key={i}>
          {rendered}
        </p>
      );
    });
  };

  return (
    <div className="explainer">
      <h2>Concept Overview</h2>
      {parseMarkdown(text)}
    </div>
  );
}

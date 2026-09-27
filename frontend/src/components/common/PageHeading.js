import { useRef, useEffect } from 'react';
export function PageHeading({ eyebrow, title, children, action }) {
  const heading = useRef(null);
  useEffect(() => {
    heading.current?.focus({
      preventScroll: true,
    });
  }, []);
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1 tabIndex="-1" ref={heading}>
          {title}
        </h1>
        {children && <p className="muted">{children}</p>}
      </div>
      {action}
    </div>
  );
}

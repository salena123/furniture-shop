import { useEffect, useState } from 'react';
import { useResource } from '../../hooks/useResource';
import { useAction } from '../../hooks/useAction';
import { api } from '../../services/api';
import { PageHeading } from '../../components/common/PageHeading';
import { ErrorNotice, LoadState } from '../../components/common/Feedback';
import { AboutContent } from '../../components/common/AboutContent';
import { ProductImage } from '../../components/common/ProductImage';
import { AboutTextEditor } from '../../components/admin/AboutTextEditor';

let nextBlockId = 0;
const withId = (block) => ({ ...block, editorId: ++nextBlockId });

function AboutEditor({ initial }) {
  const [title, setTitle] = useState(initial.title);
  const [blocks, setBlocks] = useState(() => initial.blocks.map(withId));
  const [preview, setPreview] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [saved, setSaved] = useState(false);
  const [removed, setRemoved] = useState(null);
  const action = useAction();
  useEffect(() => {
    if (!dirty) return;
    const warn = (event) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [dirty]);
  const changed = () => {
    setDirty(true);
    setSaved(false);
  };
  const update = (index, patch) => {
    setBlocks((items) => items.map((block, i) => (i === index ? { ...block, ...patch } : block)));
    changed();
  };
  const move = (index, direction) => {
    setBlocks((items) => {
      const result = [...items];
      [result[index], result[index + direction]] = [result[index + direction], result[index]];
      return result;
    });
    changed();
  };
  const page = { title, blocks: blocks.map(({ editorId, ...block }) => block) };
  const upload = (event) => {
    const file = event.target.files[0];
    event.target.value = '';
    if (!file) return;
    action.run(
      async () => {
        if (file.size > 10 * 1024 * 1024)
          throw new Error('Размер фотографии не должен превышать 10 МБ.');
        const body = new FormData();
        body.append('file', file);
        return api('/api/site/about/images', { method: 'POST', auth: true, body });
      },
      (image) => {
        setBlocks((items) => [
          ...items,
          withId({ type: 'image', image_url: image.image_url, caption: '', alt: '' }),
        ]);
        changed();
      },
    );
  };
  return (
    <div className="about-editor">
      <p className="muted">
        Соберите страницу из текста и фотографий. Изменения появятся на сайте после публикации.
        Неопубликованные правки не сохраняются при переходе на другую страницу.
      </p>
      <ErrorNotice message={action.error} />
      {saved && (
        <p role="status" className="notice success-notice">
          Страница опубликована
        </p>
      )}
      {action.busy && <p role="status">Сохраняем…</p>}
      <fieldset disabled={action.busy} className="about-editor-fields">
        <div className="about-toolbar">
          <button
            type="button"
            className="button secondary"
            aria-pressed={preview}
            onClick={() => setPreview(!preview)}
          >
            {preview ? 'Вернуться к редактированию' : 'Предпросмотр'}
          </button>
          <button
            type="button"
            className="button primary"
            disabled={!title.trim()}
            onClick={() =>
              action.run(
                () => api('/api/site/about', { method: 'PUT', auth: true, body: page }),
                () => {
                  setDirty(false);
                  setSaved(true);
                },
              )
            }
          >
            Сохранить и опубликовать
          </button>
        </div>
        {preview ? (
          <div className="surface padded">
            <AboutContent page={page} />
          </div>
        ) : (
          <>
            <label htmlFor="about-title">Заголовок страницы</label>
            <input
              id="about-title"
              value={title}
              maxLength={200}
              required
              onChange={(event) => {
                setTitle(event.target.value);
                changed();
              }}
            />
            {blocks.map((block, index) => (
              <section className="surface padded about-edit-block" key={block.editorId}>
                <div className="about-block-heading">
                  <h2>
                    {index + 1}. {block.type === 'text' ? 'Текст' : 'Фотография'}
                  </h2>
                  <div className="about-toolbar">
                    <button
                      type="button"
                      disabled={index === 0}
                      aria-label={`Блок ${index + 1} выше`}
                      onClick={() => move(index, -1)}
                    >
                      ↑ Выше
                    </button>
                    <button
                      type="button"
                      disabled={index === blocks.length - 1}
                      aria-label={`Блок ${index + 1} ниже`}
                      onClick={() => move(index, 1)}
                    >
                      ↓ Ниже
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setRemoved({ block, index });
                        setBlocks((items) =>
                          items.filter((item) => item.editorId !== block.editorId),
                        );
                        changed();
                      }}
                    >
                      Убрать блок {index + 1}
                    </button>
                  </div>
                </div>
                {block.type === 'text' ? (
                  <AboutTextEditor
                    id={`text-${block.editorId}`}
                    value={block.text}
                    onChange={(text) => update(index, { text })}
                  />
                ) : (
                  <>
                    <ProductImage className="about-edit-photo" image={block} />
                    <label htmlFor={`caption-${block.editorId}`}>Подпись к фотографии</label>
                    <input
                      id={`caption-${block.editorId}`}
                      value={block.caption}
                      maxLength={500}
                      onChange={(event) => update(index, { caption: event.target.value })}
                    />
                    <label htmlFor={`alt-${block.editorId}`}>
                      Описание изображения для доступности
                    </label>
                    <input
                      id={`alt-${block.editorId}`}
                      value={block.alt}
                      maxLength={300}
                      onChange={(event) => update(index, { alt: event.target.value })}
                    />
                  </>
                )}
              </section>
            ))}
            {removed && (
              <button
                type="button"
                className="text-button"
                disabled={blocks.length >= 50}
                onClick={() => {
                  setBlocks((items) => {
                    const result = [...items];
                    result.splice(removed.index, 0, removed.block);
                    return result;
                  });
                  setRemoved(null);
                  changed();
                }}
              >
                Вернуть последний удалённый блок
              </button>
            )}
            <div className="about-toolbar">
              <button
                type="button"
                className="button secondary"
                disabled={blocks.length >= 50}
                onClick={() => {
                  setBlocks((items) => [...items, withId({ type: 'text', text: '' })]);
                  changed();
                }}
              >
                Добавить текст
              </button>
              <label className="about-upload">
                Добавить фотографию (JPG, PNG, WebP — до 10 МБ)
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  disabled={blocks.length >= 50}
                  onChange={upload}
                />
              </label>
            </div>
          </>
        )}
      </fieldset>
    </div>
  );
}

export function AboutEditorPage() {
  const resource = useResource('/api/site/about');
  return (
    <>
      <PageHeading title="Страница «О нас»" />
      <LoadState resource={resource} />
      {resource.data && <AboutEditor initial={resource.data} />}
    </>
  );
}

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { AboutEditorPage } from './AboutEditorPage';
import { AboutPage } from '../public/AboutPage';
import { FormattedText } from '../../components/common/AboutContent';

let stored;
let failSave;
beforeEach(() => {
  stored = { title: 'О нас', configured: false, blocks: [{ type: 'text', text: 'Мастерская' }] };
  failSave = false;
  global.fetch = jest.fn(async (url, options = {}) => {
    if (options.method === 'POST')
      return {
        ok: true,
        status: 201,
        json: async () => ({ image_url: '/static/uploads/about/' + 'a'.repeat(32) + '.png' }),
      };
    if (options.method === 'PUT') {
      if (failSave)
        return { ok: false, status: 500, json: async () => ({ detail: 'Ошибка публикации' }) };
      stored = { ...JSON.parse(options.body), configured: true };
    }
    return { ok: true, status: 200, json: async () => stored };
  });
});
afterEach(() => {
  delete global.fetch;
});

test('format, upload, reorder and preview without publishing, then publish to the public page', async () => {
  const editor = render(<AboutEditorPage />);
  const text = await screen.findByLabelText('Текст блока');
  text.setSelectionRange(0, text.value.length);
  fireEvent.click(screen.getByRole('button', { name: 'Жирный', exact: true }));
  expect(text).toHaveValue('**Мастерская**');
  fireEvent.change(screen.getByLabelText(/Добавить фотографию/), {
    target: { files: [new File(['image'], 'photo.png', { type: 'image/png' })] },
  });
  fireEvent.change(await screen.findByLabelText('Подпись к фотографии'), {
    target: { value: 'Наш цех' },
  });
  fireEvent.change(screen.getByLabelText('Описание изображения для доступности'), {
    target: { value: 'Станок' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Блок 2 выше' }));
  fireEvent.click(screen.getByRole('button', { name: 'Предпросмотр' }));
  expect(screen.getByText('Мастерская').tagName).toBe('STRONG');
  expect(stored.blocks).toHaveLength(1);
  expect(stored.configured).toBe(false);
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить и опубликовать' }));
  await screen.findByText('Страница опубликована');
  expect(stored.blocks[0].type).toBe('image');
  expect(stored.blocks[0].editorId).toBeUndefined();
  editor.unmount();
  render(<AboutPage onEnquiry={jest.fn()} />);
  expect(await screen.findByAltText('Станок')).toHaveAttribute(
    'src',
    expect.stringContaining('/static/uploads/about/'),
  );
  expect(screen.getByText('Наш цех')).toBeInTheDocument();
  expect(screen.getByText('Мастерская').tagName).toBe('STRONG');
});

test('failed publication keeps edits; block removal can be undone', async () => {
  failSave = true;
  render(<AboutEditorPage />);
  fireEvent.change(await screen.findByLabelText('Заголовок страницы'), {
    target: { value: 'Новый заголовок' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Убрать блок 1' }));
  expect(screen.queryByLabelText('Текст блока')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Вернуть последний удалённый блок' }));
  expect(screen.getByLabelText('Текст блока')).toHaveValue('Мастерская');
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить и опубликовать' }));
  await screen.findByText('Ошибка публикации');
  expect(screen.getByLabelText('Заголовок страницы')).toHaveValue('Новый заголовок');
  failSave = false;
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить и опубликовать' }));
  await waitFor(() => expect(stored.title).toBe('Новый заголовок'));
});

test('formatted text supports headings, lists and safe links without executing HTML', () => {
  const { container } = render(
    <FormattedText
      text={
        '## Заголовок\n- Пункт\n- Ещё пункт\n1. Первый\n2. Второй\n*Курсив*\n[Каталог](#/catalog)\n[Опасно](javascript:alert)\n<img src=x onerror=alert(1)>'
      }
    />,
  );
  expect(screen.getByRole('heading', { name: 'Заголовок' })).toBeInTheDocument();
  expect(screen.getAllByRole('listitem')).toHaveLength(4);
  expect(screen.getByText('Курсив').tagName).toBe('EM');
  expect(screen.getAllByRole('link')).toHaveLength(1);
  expect(screen.getByRole('link')).toHaveAttribute('href', '#/catalog');
  expect(container.querySelector('img')).toBeNull();
});

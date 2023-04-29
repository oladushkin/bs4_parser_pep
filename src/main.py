import re
from urllib.parse import urljoin
from outputs import control_output
import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = session.get(whats_new_url)
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(
        main_div, 'div',
        attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = session.get(version_link)
        response.encoding = 'utf-8'
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append(
            (version_link, h1.text, dl_text)
        )
    print(result)
    return result


def latest_versions(session):
    response = session.get(MAIN_DOC_URL)
    response.encoding = 'utf-8'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Не найден список c версиями Python')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = session.get(downloads_url)
    response.encoding = 'utf-8'
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = session.get(PEP_DOC_URL)
    response = get_response(session, PEP_DOC_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    page = find_tag(soup, 'section', attrs={'id': 'index-by-category'})
    tables_tag = page.find_all('tr')
    result = {}
    total = 0
    for tr in tqdm(tables_tag[1:]):
        abbr_status = tr.find_all('abbr')
        if abbr_status == []:
            continue
        if len(abbr_status[0].text) > 1:
            status = abbr_status[0].text[1:]
        else:
            status = abbr_status[0].text
        if status not in EXPECTED_STATUS:
            continue
        link = tr.find('a', )
        href = link['href']
        status_link = urljoin(PEP_DOC_URL, href)
        response = session.get(status_link)
        response.encoding = 'utf-8'
        response = get_response(session, status_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        status_pep = soup.find(
            string='Status'
        ).parent.find_next_sibling(
            'dd'
        ).string
        if status_pep not in EXPECTED_STATUS[status]:
            logging.info(
                f'Несовпадающие статусы: '
                f' {status_link}'
                f' Статус в карточке: {status_pep}'
                f' Ожидаемые статусы: {EXPECTED_STATUS[status]}'
            )
        if status_pep not in result:
            result[status_pep] = 1
        else:
            result[status_pep] += 1
        total += 1
    table_result = [('Статус', 'Количество')]
    for kay, count in result.items():
        table_result.append((kay, count))
        total += 1
    table_result.append(('Total', total))
    return table_result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()

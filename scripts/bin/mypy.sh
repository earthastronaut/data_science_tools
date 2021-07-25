#!/bin/bash
set -e
ROOT_PATH=$(git rev-parse --show-toplevel)
mypy --config-file=${ROOT_PATH}/scripts/config/mypy.ini $@

python -c "print('Generate mypy badge') ;\
    import lxml.html ;\
    report_path = '${ROOT_PATH}/docs/reports/mypy-report/index.html' ;\
    badge_path = '${ROOT_PATH}/docs/badges/mypy.svg' ;\
    '# Read report path' ;\
    page = lxml.html.parse(report_path) ;\
    text = page.xpath('//body//table[1]//tfoot//tr[1]//th[2]')[0].text ;\
    percentage, _, info = text.partition('%') ;\
    percentage = float(percentage) ;\
    text = format(percentage, '.0f') + _ + info ;\
    '# Read+update badge' ;\
    brightgreen, green, yellow, orange, red = '#4c1', '#97CA00', '#dfb317', '#fe7d37', '#e05d44' ;\
    color = brightgreen if (percentage > 99) else green if (percentage > 75) else yellow if (percentage > 50) else orange if (percentage > 25) else red ;\
    tree = lxml.etree.parse(badge_path) ;\
    ns = {'s': 'http://www.w3.org/2000/svg'} ;\
    tree.xpath('//s:g[2]//s:text', namespaces=ns)[2].attrib['fill'] = color ;\
    tree.xpath('//s:g[2]//s:text', namespaces=ns)[2].text = text ;\
    tree.xpath('//s:g[2]//s:text', namespaces=ns)[3].text = text ;\
    tree.write(badge_path) ;\
    print(text)"

#!/bin/bash
set -e
MIN_COVERAGE_PERCENT=70
ROOT_PATH=$(git rev-parse --show-toplevel)
CONFIG_PATH=${ROOT_PATH}/scripts/config/coveragerc.ini
COVERAGE_REPORT_PATH=${ROOT_PATH}/docs/coverage.report
COVERAGE_BADGE_PATH=${ROOT_PATH}/docs/badges/coverage.svg

coverage run --rcfile=${CONFIG_PATH} -m pytest --verbose $@

coverage html --rcfile=${CONFIG_PATH}

coverage report --rcfile=${CONFIG_PATH} > ${COVERAGE_REPORT_PATH}

cat ${COVERAGE_REPORT_PATH}

# check coverage and update badge
echo ${MIN_COVERAGE_PERCENT} | python -c "min_percentage = int(input('')); \
    from xml.etree.ElementTree import ElementTree; \
    percentage = int(open('${COVERAGE_REPORT_PATH}').read().split('\n')[-2].split()[-1].strip('%')); \
    brightgreen, green, yellow, orange, red = '#4c1', '#97CA00', '#dfb317', '#fe7d37', '#e05d44'; \
    color = brightgreen if (percentage > 99) else green if (percentage > 75) else yellow if (percentage > 50) else orange if (percentage > 25) else red; \
    svg_file = '${COVERAGE_BADGE_PATH}'; \
    ns = {'s': 'http://www.w3.org/2000/svg'}; \
    tree = ElementTree(file=svg_file); \
    tree.findall('s:g', ns)[0].findall('s:path', ns)[1].attrib['fill'] = color; \
    tree.findall('s:g', ns)[1].findall('s:text', ns)[2].text = str(percentage) + '%'; \
    tree.findall('s:g', ns)[1].findall('s:text', ns)[3].text = str(percentage) + '%'; \
    tree.write(svg_file); \
    assert percentage >= min_percentage, 'Total {}% less than minimum {}%, please add test coverage'.format(percentage, min_percentage); \
    print('\n\nTests passed with coverage {}% >= {}%'.format(percentage, min_percentage)); \
    "

from logging import INFO, LogRecord

from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm_logging.formatters import ExtraConsoleFormatter


def test_extra_formatter_formats_simple_log():
    format_string = "{message}"
    formatter = ExtraConsoleFormatter(format_string)

    log_record = LogRecord('name', INFO, 'some_function', 42, "A sample log.", None, None)
    log_result = formatter.format(log_record)
    assert_that(log_result, is_(equal_to("A sample log.")))


def test_extra_formatter_formats_log_with_extra():
    format_string = "{message}"
    formatter = ExtraConsoleFormatter(format_string)

    log_message = "A sample log with extra: {foo}."
    extra = dict(foo='bar')

    log_record = LogRecord(
        'name',
        INFO,
        'some_function',
        42,
        log_message,
        None,
        None
    )
    log_record.foo = extra['foo']

    log_result = formatter.format(log_record)
    assert_that(log_result, is_(equal_to(log_message.format(**extra))))


def test_extra_formatter_respects_old_style_formatting():
    format_string = "{message}"
    formatter = ExtraConsoleFormatter(format_string)

    log_message = "A sample log with old string %s."
    args = ("bar",)

    log_record = LogRecord(
        'name',
        INFO,
        'some_function',
        42,
        log_message,
        args,
        0
    )

    log_result = formatter.format(log_record)
    assert_that(log_result, is_(equal_to(log_message % args)))


def test_extra_formatter_supports_old_and_new_formats():
    format_string = "{message}"
    formatter = ExtraConsoleFormatter(format_string)

    log_message = "A sample log with old string %s, new: {foo}"
    args = ("bar",)
    extra = dict(foo="baz")

    log_record = LogRecord(
        'name',
        INFO,
        'some_function',
        42,
        log_message,
        args,
        0
    )
    log_record.foo = extra['foo']

    log_result = formatter.format(log_record)
    assert_that(log_result, is_(equal_to(log_message.format(**extra) % args)))


def test_extra_formatter_does_not_mangle_dict_as_message():
    format_string = "{message}"
    formatter = ExtraConsoleFormatter(format_string)

    log_message = dict(foo='bar')

    log_record = LogRecord(
        'name',
        INFO,
        'some_function',
        42,
        log_message,
        None,
        0
    )

    log_result = formatter.format(log_record)
    assert_that(log_result, is_(equal_to(str(log_message))))


def test_extra_formatter_ignores_key_errors():
    format_string = "{message}"
    formatter = ExtraConsoleFormatter(format_string)

    log_message = '{i am a teapot}'

    log_record = LogRecord(
        'name',
        INFO,
        'some_function',
        42,
        log_message,
        None,
        0
    )

    log_result = formatter.format(log_record)
    assert_that(log_result, is_(equal_to(str(log_message))))

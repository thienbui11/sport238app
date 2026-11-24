package com.sportshop.web;

public class BadRequestException extends RuntimeException {
    public BadRequestException(String code) { super(code); }
}

package com.example.realestate;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * [Spring Boot 애플리케이션의 시작점(Main Class)]
 *
 * @SpringBootApplication 어노테이션은 아래의 3가지 핵심 기능을 통합한 어노테이션입니다:
 * 1. @EnableAutoConfiguration: Spring Boot의 자동 설정(데이터베이스 연동, Web MVC 설정 등)을 활성화
 * 2. @ComponentScan: 현재 패키지(com.example.realestate) 및 하위 패키지에서 @Component, @Service, @Repository, @Controller 등을 자동으로 탐색하여 빈(Bean)으로 등록
 * 3. @Configuration: 스프링 설정 클래스임을 명시
 */
@SpringBootApplication
public class ScraperBackendApplication {

    /**
     * 자바 프로그램 실행 시 가장 먼저 호출되는 메인(main) 메서드입니다.
     * 
     * @param args 실행 시 전달되는 커맨드라인 아규먼트
     */
    public static void main(String[] args) {
        // SpringApplication.run() 메서드를 호출하여 내장된 톰캣(Tomcat) 서버를 구동하고,
        // 스프링 컨테이너(ApplicationContext)를 초기화합니다.
        SpringApplication.run(ScraperBackendApplication.class, args);
    }
}

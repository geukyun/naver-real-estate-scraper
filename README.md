# Homepage Project

이 프로젝트는 Spring Boot 기반으로 작성된 홈페이지 애플리케이션입니다.

## ? 시작하기 (Getting Started)

### 사전 요구사항 (Prerequisites)
- Java 17 (또는 설정된 Java 버전)
- Gradle 또는 Maven (빌드 도구)

### 로컬 환경에서 실행하기 (Running locally)
프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 애플리케이션을 구동할 수 있습니다.

**Gradle 사용 시:**
```bash
./gradlew bootRun
```
*(Windows 환경에서는 `gradlew.bat bootRun`을 사용하세요)*

**Maven 사용 시:**
```bash
./mvnw spring-boot:run
```
*(Windows 환경에서는 `mvnw.cmd spring-boot:run`을 사용하세요)*

## ? 사용 기술 (Tech Stack)
- **Framework:** Spring Boot
- **Language:** Java

## ? 프로젝트 구조 (Project Structure)
- `src/main/java` : 애플리케이션의 핵심 비즈니스 로직 (Controller, Service, Repository 등)
- `src/main/resources` : 설정 파일 (`application.properties` 또는 `application.yml`) 및 정적 리소스 (HTML, CSS, JS)
- `src/test/java` : 단위 및 통합 테스트 코드

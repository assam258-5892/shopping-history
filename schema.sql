
-- ================================
-- 품목 테이블: 상품 정보
-- ================================
CREATE TABLE 품목 (
    코드 TEXT PRIMARY KEY,         -- 품목 고유 코드
    품목명 TEXT NOT NULL,          -- 품목명
    규격 TEXT                      -- 규격(예: 500ml, 1박스 등)
);

-- ================================
-- 구매 테이블: 구매자 정보
-- ================================
CREATE TABLE 구매 (
    번호 INTEGER PRIMARY KEY AUTOINCREMENT, -- 구매자 고유 번호
    구매자명 TEXT NOT NULL UNIQUE           -- 구매자 이름
);

-- =====================================
-- 매장 테이블: 매장 정보 및 위치
-- =====================================
CREATE TABLE 매장 (
    번호 INTEGER PRIMARY KEY AUTOINCREMENT, -- 매장 고유 번호
    매장명 TEXT NOT NULL UNIQUE,            -- 매장 이름
    위도 REAL,                              -- 위도(latitude)
    경도 REAL                               -- 경도(longitude)
);

-- =====================================
-- 구매기록 테이블: 실제 구매 내역
-- =====================================
CREATE TABLE 구매기록 (
    일련번호 INTEGER PRIMARY KEY AUTOINCREMENT, -- 구매기록 고유 번호
    구매일자 TEXT NOT NULL,                     -- 구매 일자 (YYYY-MM-DD)
    품목코드 TEXT NOT NULL,                     -- 구매한 품목 코드
    수량 INTEGER NOT NULL,                      -- 구매 수량
    가격 INTEGER NOT NULL,                      -- 단가(원)
    할인금액 INTEGER NOT NULL,                  -- 할인 금액(원)
    구매금액 INTEGER NOT NULL,                  -- 실구매 금액(수량*가격-할인금액)
    구매자번호 INTEGER,                         -- 구매자 번호(구매 테이블 참조)
    매장번호 INTEGER,                           -- 매장 번호(매장 테이블 참조)
    FOREIGN KEY (품목코드) REFERENCES 품목(코드),
    FOREIGN KEY (구매자번호) REFERENCES 구매(번호),
    FOREIGN KEY (매장번호) REFERENCES 매장(번호)
);

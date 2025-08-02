document.addEventListener('DOMContentLoaded', function() {
    const 품목코드 = document.getElementById('품목코드');
    const 품목명 = document.getElementById('품목명');
    const 규격 = document.getElementById('규격');

    // 직접 입력 시 faded 제거 (검은색)
    if (품목명) {
        품목명.addEventListener('input', function() {
            if (품목명.value.trim()) {
                품목명.classList.remove('placeholder-faded');
            } else {
                품목명.classList.add('placeholder-faded');
            }
        });
    }
    if (규격) {
        규격.addEventListener('input', function() {
            if (규격.value.trim()) {
                규격.classList.remove('placeholder-faded');
            } else {
                규격.classList.add('placeholder-faded');
            }
        });
    }

    품목코드.addEventListener('input', async function() {
        const code = 품목코드.value;
        if (!code) {
            품목명.placeholder = '필수 입력';
            품목명.classList.add('placeholder-faded');
            // 기존 값은 그대로 둠
            if (규격) {
                규격.value = '';
                규격.placeholder = '필수 입력';
                규격.classList.add('placeholder-faded');
            }
            return;
        }
        try {
            const resp = await fetch(`/api/item-name/${encodeURIComponent(code)}`);
            if (resp.ok) {
                const data = await resp.json();
                if (data.품목명) {
                    품목명.value = data.품목명;
                    품목명.placeholder = '';
                    품목명.classList.remove('placeholder-faded');
                } else {
                    품목명.placeholder = '코드에 해당하는 품목 없음';
                    품목명.classList.add('placeholder-faded');
                    // 기존 값은 그대로 둠
                }
                if (규격) {
                        if (data.규격) {
                            규격.value = data.규격;
                            규격.placeholder = '';
                            규격.classList.remove('placeholder-faded');
                        } else {
                            규격.placeholder = '코드에 해당하는 규격 없음';
                            규격.classList.add('placeholder-faded');
                            // 기존 값은 그대로 둡니다.
                        }
                }
            } else {
                품목명.placeholder = '조회 오류';
                품목명.classList.add('placeholder-faded');
                if (규격) {
                        규격.placeholder = '조회 오류';
                        규격.classList.add('placeholder-faded');
                        // 기존 값은 그대로 둡니다.
                }
            }
        } catch {
            품목명.placeholder = '조회 오류';
            품목명.classList.add('placeholder-faded');
            if (규격) {
                    규격.placeholder = '조회 오류';
                    규격.classList.add('placeholder-faded');
                    // 기존 값은 그대로 둡니다.
            }
        }
    });
});

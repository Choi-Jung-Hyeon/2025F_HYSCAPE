#!/bin/bash
# ============================================================================
# H2HUB 브리핑 자동화 시스템
# ============================================================================
# 설명: PDF 브리핑 자동 분석 및 Notion 업로드
# 작성자: Hyscape Intern
# 버전: 2.0
# ============================================================================

set -euo pipefail  # 엄격한 오류 처리

# ===== 색상 정의 =====
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# ===== 경로 설정 =====
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PDF_DIR="${PDF_DIR:-$SCRIPT_DIR/../pdf}"
readonly ARCHIVE_DIR="${ARCHIVE_DIR:-$SCRIPT_DIR/../pdf_archive}"
readonly LOG_DIR="$SCRIPT_DIR/logs"
readonly LOG_FILE="$LOG_DIR/automation_$(date +%Y%m%d_%H%M%S).log"

# ===== 설정 =====
DRY_RUN=false
VERBOSE=false
BACKUP=true
PAGES_TO_CRAWL=0  # 0 = 기존 PDF만, >0 = 웹 크롤링

# ===== 함수: 로깅 =====
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}ℹ️  $@${NC}"
    log "INFO" "$@"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $@${NC}"
    log "WARN" "$@"
}

log_error() {
    echo -e "${RED}❌ $@${NC}"
    log "ERROR" "$@"
}

log_success() {
    echo -e "${GREEN}✅ $@${NC}"
    log "SUCCESS" "$@"
}

# ===== 함수: 초기화 =====
init_dirs() {
    log_info "디렉토리 초기화..."
    mkdir -p "$ARCHIVE_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$PDF_DIR"
}

# ===== 함수: 환경 검증 =====
check_environment() {
    log_info "환경 검증 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # 필수 파일 확인
    local required_files=("config.py" "main.py" "article_analyzer.py" "notion_uploader.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$SCRIPT_DIR/$file" ]; then
            log_error "필수 파일이 없습니다: $file"
            exit 1
        fi
    done
    
    # 가상환경 활성화
    if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
        log_info "가상환경 활성화..."
        source "$SCRIPT_DIR/venv/bin/activate"
    else
        log_warn "가상환경이 없습니다. 전역 Python 사용"
    fi
    
    log_success "환경 검증 완료"
}

# ===== 함수: PDF 개수 확인 =====
count_pdfs() {
    find "$PDF_DIR" -maxdepth 1 -name "*.pdf" -type f | wc -l
}

# ===== 함수: 백업 생성 =====
create_backup() {
    if [ "$BACKUP" = true ]; then
        local backup_dir="$SCRIPT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        if [ $(count_pdfs) -gt 0 ]; then
            log_info "백업 생성 중... → $backup_dir"
            cp "$PDF_DIR"/*.pdf "$backup_dir/" 2>/dev/null || true
            log_success "백업 완료: $(count_pdfs)개 파일"
        fi
    fi
}

# ===== 함수: 메인 실행 =====
run_automation() {
    log_info "자동화 시작..."
    echo ""
    
    # 크롤링 모드
    if [ "$PAGES_TO_CRAWL" -gt 0 ]; then
        log_info "웹 크롤링 모드: $PAGES_TO_CRAWL 페이지"
        
        if [ "$DRY_RUN" = true ]; then
            log_warn "[DRY RUN] python main.py --pages $PAGES_TO_CRAWL"
        else
            python "$SCRIPT_DIR/main.py" --pages "$PAGES_TO_CRAWL" 2>&1 | tee -a "$LOG_FILE"
        fi
    else
        # 기존 PDF 처리 모드
        local pdf_count=$(count_pdfs)
        
        if [ "$pdf_count" -eq 0 ]; then
            log_warn "처리할 PDF 파일이 없습니다: $PDF_DIR"
            log_info "웹 크롤링을 원하시면: --pages N 옵션 사용"
            return 0
        fi
        
        log_info "$pdf_count개의 PDF 파일 발견"
        
        if [ "$DRY_RUN" = true ]; then
            log_warn "[DRY RUN] python main.py --existing-pdfs $PDF_DIR"
            find "$PDF_DIR" -name "*.pdf" -exec basename {} \; | while read file; do
                echo "  - $file"
            done
        else
            python "$SCRIPT_DIR/main.py" --existing-pdfs "$PDF_DIR" 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
}

# ===== 함수: 아카이브 =====
archive_pdfs() {
    local pdf_count=$(count_pdfs)
    
    if [ "$pdf_count" -eq 0 ]; then
        return 0
    fi
    
    log_info "처리된 PDF 아카이브..."
    
    local archived=0
    for pdf_file in "$PDF_DIR"/*.pdf; do
        if [ -f "$pdf_file" ]; then
            local filename=$(basename "$pdf_file")
            
            if [ "$DRY_RUN" = true ]; then
                log_warn "[DRY RUN] $filename → pdf_archive/"
            else
                mv "$pdf_file" "$ARCHIVE_DIR/"
                log_info "  ✓ $filename → pdf_archive/"
            fi
            
            ((archived++))
        fi
    done
    
    log_success "$archived개 파일 아카이브 완료"
}

# ===== 함수: 요약 출력 =====
print_summary() {
    echo ""
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${GREEN}🎉 자동화 완료!${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${GREEN}📊 실행 정보:${NC}"
    echo -e "   - 실행 시간: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "   - PDF 디렉토리: $PDF_DIR"
    echo -e "   - 아카이브: $ARCHIVE_DIR"
    echo -e "   - 로그 파일: $LOG_FILE"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}   - 모드: DRY RUN (실제 실행 안 함)${NC}"
    fi
    
    echo -e "${BLUE}======================================================================${NC}"
    echo ""
}

# ===== 함수: 사용법 =====
usage() {
    cat << EOF
사용법: $0 [옵션]

옵션:
    --pages N          웹에서 N 페이지 크롤링 (기본값: 0 = 기존 PDF만)
    --dry-run          실제 실행 없이 테스트
    --no-backup        백업 생성 안 함
    --verbose          상세 로그 출력
    --help             이 도움말 출력

예시:
    $0                          # 기존 PDF 처리
    $0 --pages 3                # 웹에서 3페이지 크롤링
    $0 --dry-run                # 테스트 실행
    $0 --pages 1 --no-backup    # 1페이지 크롤링, 백업 안 함

환경변수:
    PDF_DIR            PDF 디렉토리 경로 (기본값: ../pdf)
    ARCHIVE_DIR        아카이브 디렉토리 (기본값: ../pdf_archive)

EOF
    exit 0
}

# ===== 함수: 에러 핸들러 =====
error_handler() {
    local line_no=$1
    log_error "스크립트 오류 발생 (라인: $line_no)"
    log_error "로그 파일 확인: $LOG_FILE"
    exit 1
}

trap 'error_handler ${LINENO}' ERR

# ===== 메인: 인자 파싱 =====
while [[ $# -gt 0 ]]; do
    case $1 in
        --pages)
            PAGES_TO_CRAWL="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-backup)
            BACKUP=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            set -x
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            usage
            ;;
    esac
done

# ===== 메인: 실행 =====
main() {
    # 헤더
    echo -e "${GREEN}======================================================================${NC}"
    echo -e "${GREEN}🚀 H2HUB 브리핑 자동화 시스템 v2.0${NC}"
    echo -e "${GREEN}======================================================================${NC}"
    echo ""
    
    # 초기화
    init_dirs
    check_environment
    
    # 백업
    create_backup
    
    # 실행
    run_automation
    
    # 성공 시 아카이브
    if [ $? -eq 0 ]; then
        archive_pdfs
        print_summary
    else
        log_error "자동화 실패. PDF는 이동하지 않았습니다."
        exit 1
    fi
}

# 실행
main "$@"
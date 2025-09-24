"""
Appointment entity representing a medical appointment.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field, field_validator

from src.domain.base import Entity
from src.domain.entities.tag import TagReference


class Appointment(Entity):
    """
    Appointment entity representing a scheduled medical consultation.

    This entity contains all essential information about a medical appointment
    imported from Excel files.
    """

    # Required fields
    nome_unidade: str = Field(..., description="Nome da Unidade de Saúde")
    nome_marca: str = Field(..., description="Nome da Marca/Clínica")
    nome_paciente: str = Field(..., description="Nome completo do paciente")
    data_agendamento: Optional[datetime] = Field(
        None, description="Data do agendamento"
    )
    hora_agendamento: Optional[str] = Field(
        None, description="Hora do agendamento (HH:MM)"
    )

    # Optional fields
    tipo_consulta: Optional[str] = Field(
        None, description="Tipo de consulta médica"
    )
    cip: Optional[str] = Field(
        None,
        description="Código CIP (Classificação Internacional de Procedimentos)",
    )
    status: Optional[str] = Field(
        "Pendente", description="Status do agendamento"
    )
    telefone: Optional[str] = Field(
        None, description="Telefone de contato do paciente"
    )
    carro: Optional[str] = Field(
        None, description="Informações do carro utilizado"
    )
    observacoes: Optional[str] = Field(
        None, description="Observações adicionais"
    )
    driver_id: Optional[str] = Field(
        None, description="ID do motorista responsável pela coleta"
    )
    collector_id: Optional[str] = Field(
        None, description="ID da coletora responsável pela coleta"
    )
    car_id: Optional[str] = Field(
        None, description="ID do carro utilizado na coleta"
    )
    # Campos adicionais de endereço/convenio
    # (podem não existir em todas as planilhas)
    cep: Optional[str] = Field(None, description="CEP do endereço de coleta")
    endereco_coleta: Optional[str] = Field(
        None, description="Endereço da coleta"
    )
    endereco_completo: Optional[str] = Field(
        None, description="Endereço completo não normalizado da planilha"
    )
    endereco_normalizado: Optional[Dict[str, Optional[str]]] = Field(
        None, description="Endereço normalizado em campos estruturados"
    )
    # Campos de documento do paciente
    documento_completo: Optional[str] = Field(
        None, description="Documento completo não normalizado da planilha"
    )
    documento_normalizado: Optional[Dict[str, Optional[str]]] = Field(
        None, description="Documentos normalizados (CPF e RG estruturados)"
    )
    cpf: Optional[str] = Field(
        None, description="CPF do paciente (apenas dígitos)"
    )
    rg: Optional[str] = Field(
        None, description="RG do paciente (apenas dígitos)"
    )
    numero_convenio: Optional[str] = Field(
        None, description="Número do convênio"
    )
    nome_convenio: Optional[str] = Field(None, description="Nome do convênio")
    carteira_convenio: Optional[str] = Field(
        None, description="Número da carteira do convênio"
    )
    cadastrado_por: Optional[str] = Field(
        None, description="Usuário responsável pelo cadastro do agendamento"
    )
    agendado_por: Optional[str] = Field(
        None, description="Usuário responsável por mover o status para Agendado"
    )
    tags: List[TagReference] = Field(
        default_factory=list,
        description="Tags associadas ao agendamento",
    )
    canal_confirmacao: Optional[str] = Field(
        None,
        description="Canal utilizado para confirmação (ex.: WhatsApp, Tel)",
    )
    data_confirmacao: Optional[datetime] = Field(
        None, description="Data da confirmação do agendamento"
    )
    hora_confirmacao: Optional[str] = Field(
        None, description="Hora da confirmação (HH:MM)"
    )

    # Metadata fields (handled by Entity base class)
    # created_at: datetime
    # updated_at: datetime

    @field_validator("nome_unidade", "nome_marca", "nome_paciente")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        """Validate that required string fields are not empty."""
        if not value or not value.strip():
            raise ValueError("Campo obrigatório não pode estar vazio")
        return value.strip()

    @field_validator("hora_agendamento")
    @classmethod
    def validate_time_format(cls, value: Optional[str]) -> Optional[str]:
        """Validate time format (HH:MM)."""
        if value is None:
            return None

        # Basic validation for HH:MM format
        trimmed = value.strip()
        if not trimmed:
            return None

        parts = trimmed.split(":")
        if len(parts) != 2:
            raise ValueError("Hora deve estar no formato HH:MM")

        try:
            hours = int(parts[0])
            minutes = int(parts[1])

            if not (0 <= hours <= 23):
                raise ValueError("Hora deve estar entre 00 e 23")
            if not (0 <= minutes <= 59):
                raise ValueError("Minutos devem estar entre 00 e 59")

            # Normalize format
            return f"{hours:02d}:{minutes:02d}"
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Hora deve conter apenas números")
            raise

    @field_validator("telefone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """Validate and normalize phone number."""
        if not value:
            return None

        # Remove common formatting characters
        phone = (
            value.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        # Brazilian phone validation (landline 10, mobile 11)
        if phone and not (10 <= len(phone) <= 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")

        return phone if phone else None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> str:
        """Validate appointment status."""
        if not value:
            return "Pendente"

        valid_statuses = [
            "Pendente",
            "Autorização",
            "Cadastrar",
            "Agendado",
            "Confirmado",
            "Coletado",
            "Alterar",
            "Cancelado",
            "Recoleta",
        ]

        if value not in valid_statuses:
            raise ValueError(
                f"Status inválido. Valores permitidos: "
                f"{', '.join(valid_statuses)}"
            )

        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: List[TagReference]) -> List[TagReference]:
        """Ensure tag identifiers are unique within the appointment."""
        seen: set[str] = set()
        unique_tags: list[TagReference] = []
        for tag in value:
            tag_id = str(tag.id)
            if tag_id not in seen:
                seen.add(tag_id)
                unique_tags.append(tag)
        return unique_tags

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "nome_unidade": "UBS Centro",
                "nome_marca": "Clínica Saúde",
                "nome_paciente": "João Silva",
                "data_agendamento": "2025-01-15T00:00:00",
                "hora_agendamento": "14:30",
                "tipo_consulta": "Clínico Geral",
                "status": "Pendente",
                "telefone": "11999887766",
                "carro": "Honda Civic Prata",
                "observacoes": "Paciente com diabetes",
                "driver_id": "507f1f77bcf86cd799439012",
                "endereco_completo": "rua maurício da costa faria,52,recreio dos bandeirantes,rio de janeiro,RJ,22790-285",
                "endereco_normalizado": {
                    "rua": "Rua Maurício da Costa Faria",
                    "numero": "52",
                    "complemento": None,
                    "bairro": "Recreio dos Bandeirantes",
                    "cidade": "Rio de Janeiro",
                    "estado": "RJ",
                    "cep": "22790-285",
                },
                "documento_completo": "CPF: 12345678901, RG: 123456789",
                "documento_normalizado": {
                    "cpf": "12345678901",
                    "rg": "123456789",
                    "cpf_formatted": "123.456.789-01",
                    "rg_formatted": "12.345.678",
                },
                "cpf": "12345678901",
                "rg": "123456789",
                "created_at": "2025-01-14T10:00:00",
                "updated_at": "2025-01-14T10:00:00",
            }
        }

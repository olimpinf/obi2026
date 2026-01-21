from django.db import models


class Escola(models.Model):
    """
    Model representing a school from INEP's Censo Escolar data.
    """
    co_entidade = models.IntegerField(
        primary_key=True,
        verbose_name="Código da Escola",
        help_text="Código único da escola no INEP"
    )
    no_entidade = models.CharField(
        max_length=100,
        verbose_name="Nome da Escola",
        db_index=True
    )
    no_municipio = models.CharField(
        max_length=150,
        verbose_name="Nome do Município",
        db_index=True
    )
    sg_uf = models.CharField(
        max_length=2,
        verbose_name="Sigla da UF",
        db_index=True
    )
    tp_dependencia = models.IntegerField(
        verbose_name="Dependência Administrativa",
        help_text="1-Federal, 2-Estadual, 3-Municipal, 4-Privada",
        null=True,
        blank=True
    )
    ds_endereco = models.CharField(
        max_length=100,
        verbose_name="Endereço",
        blank=True,
        default=""
    )
    nu_endereco = models.CharField(
        max_length=10,
        verbose_name="Número",
        blank=True,
        default=""
    )
    ds_complemento = models.CharField(
        max_length=20,
        verbose_name="Complemento",
        blank=True,
        default=""
    )
    no_bairro = models.CharField(
        max_length=50,
        verbose_name="Bairro",
        blank=True,
        default=""
    )
    co_cep = models.CharField(
        max_length=8,
        verbose_name="CEP",
        blank=True,
        default=""
    )
    nu_ddd = models.CharField(
        max_length=8,
        verbose_name="DDD",
        blank=True,
        default=""
    )
    nu_telefone = models.CharField(
        max_length=8,
        verbose_name="Telefone",
        blank=True,
        default=""
    )

    class Meta:
        db_table = 'inep'
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ['no_entidade']
        indexes = [
            models.Index(fields=['sg_uf', 'no_municipio']),
        ]

    def __str__(self):
        return f"{self.no_entidade} - {self.no_municipio}/{self.sg_uf}"

    def get_endereco_completo(self):
        """Returns the complete address as a formatted string."""
        parts = [self.ds_endereco]
        if self.nu_endereco:
            parts.append(self.nu_endereco)
        if self.ds_complemento:
            parts.append(self.ds_complemento)
        if self.no_bairro:
            parts.append(f"Bairro: {self.no_bairro}")
        if self.co_cep:
            parts.append(f"CEP: {self.co_cep}")
        return ", ".join(filter(None, parts))

    def get_telefone_completo(self):
        """Returns the complete phone number."""
        if self.nu_ddd and self.nu_telefone:
            return f"({self.nu_ddd}) {self.nu_telefone}"

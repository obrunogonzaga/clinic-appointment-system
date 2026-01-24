// MongoDB initialization script for LAB environment
// This script runs when the MongoDB container is first created

// Switch to the clinic lab database
db = db.getSiblingDB('clinic_lab_db');

// Create collections with schema validation matching the backend User entity
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'name', 'password_hash', 'is_admin', 'is_active', 'created_at'],
      properties: {
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Must be a valid email address'
        },
        name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100,
          description: 'User full name'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Hashed password is required'
        },
        is_admin: {
          bsonType: 'bool',
          description: 'Whether user has admin privileges'
        },
        is_active: {
          bsonType: 'bool',
          description: 'User active status'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: ['date', 'null'],
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('patients', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'created_at'],
      properties: {
        name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100,
          description: 'Patient full name'
        },
        email: {
          bsonType: ['string', 'null'],
          description: 'Valid email address'
        },
        phone: {
          bsonType: ['string', 'null'],
          description: 'Phone number'
        },
        date_of_birth: {
          bsonType: ['date', 'null'],
          description: 'Patient date of birth'
        },
        address: {
          bsonType: ['object', 'null'],
          properties: {
            street: { bsonType: 'string' },
            city: { bsonType: 'string' },
            state: { bsonType: 'string' },
            zip_code: { bsonType: 'string' }
          }
        },
        medical_record_number: {
          bsonType: ['string', 'null'],
          description: 'External medical record number'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: ['date', 'null'],
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('appointments', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['created_at'],
      properties: {
        id: {
          bsonType: ['string', 'null'],
          description: 'Unique appointment identifier'
        },
        nome_unidade: {
          bsonType: ['string', 'null'],
          description: 'Nome da Unidade de Saúde'
        },
        nome_marca: {
          bsonType: ['string', 'null'],
          description: 'Nome da Marca/Clínica'
        },
        nome_paciente: {
          bsonType: ['string', 'null'],
          description: 'Nome completo do paciente'
        },
        data_agendamento: {
          bsonType: ['date', 'null'],
          description: 'Data do agendamento'
        },
        hora_agendamento: {
          bsonType: ['string', 'null'],
          description: 'Hora do agendamento (HH:MM)'
        },
        tipo_consulta: {
          bsonType: ['string', 'null'],
          description: 'Tipo de consulta médica'
        },
        status: {
          bsonType: ['string', 'null'],
          description: 'Status do agendamento'
        },
        telefone: {
          bsonType: ['string', 'null'],
          description: 'Telefone de contato do paciente'
        },
        carro: {
          bsonType: ['string', 'null'],
          description: 'Informações do carro utilizado'
        },
        observacoes: {
          bsonType: ['string', 'null'],
          description: 'Observações adicionais'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: ['date', 'null'],
          description: 'Last update timestamp'
        }
      }
    }
  }
});

// Create indexes for better query performance
db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'is_admin': 1 });
db.users.createIndex({ 'is_active': 1 });

db.patients.createIndex({ 'email': 1 }, { sparse: true });
db.patients.createIndex({ 'phone': 1 }, { sparse: true });
db.patients.createIndex({ 'name': 'text' });

db.appointments.createIndex({ 'nome_unidade': 1 });
db.appointments.createIndex({ 'nome_marca': 1 });
db.appointments.createIndex({ 'nome_paciente': 'text' });
db.appointments.createIndex({ 'data_agendamento': 1 });
db.appointments.createIndex({ 'status': 1 });
db.appointments.createIndex({ 'data_agendamento': 1, 'status': 1 });
db.appointments.createIndex({ 'nome_unidade': 1, 'nome_marca': 1 });
db.appointments.createIndex({ 'id': 1 }, { unique: true, sparse: true, name: 'appointment_id_unique' });

print('MongoDB LAB initialization completed successfully!');
